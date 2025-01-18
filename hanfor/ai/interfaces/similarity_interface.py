import logging
from asyncio import Event
from hanfor.ai import AiDataEnum
from hanfor.ai.strategies.similarity_abstract_class import SimilarityAlgorithm
import os
import importlib

# Enable or disable debug logging
debug_enabled = False


def load_similarity_methods() -> dict[str, SimilarityAlgorithm]:
    """Dynamically loads all similarity algorithms from the specified directory."""

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../strategies/similarity_methods/")
    methods = {}
    base_package = "hanfor.ai.strategies.similarity_methods"

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            # Import Modul
            module_name = filename[:-3]
            module_path = f"{base_package}.{module_name}"

            try:
                module = importlib.import_module(module_path)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, SimilarityAlgorithm)
                        and attr is not SimilarityAlgorithm
                    ):
                        try:
                            instance = attr()
                            methods[instance.name] = instance
                        except TypeError as e:
                            logging.warning(f"Class {attr_name} in module {module_path} could not be instantiated: {e}")
            except ModuleNotFoundError as e:
                logging.error(f"Error loading module {module_path}: {e}")
    return methods


class ClusteringProgress:
    def __init__(self, requirements: dict, progress_status: dict, progress_update, sim_function):
        self.progress_status = progress_status
        self.progress_update = progress_update
        self.requirements = requirements
        self.function = sim_function

    def start(self, stop_event_cluster: Event, threshold: float) -> set:
        return self.__cluster_requirements_by_description(self.requirements, stop_event_cluster, threshold)

    def __update_progress(self):

        if self.progress_status[AiDataEnum.STATUS] == AiDataEnum.CLUSTERING:
            self.progress_update(
                AiDataEnum.CLUSTER, AiDataEnum.PROCESSED, (self.progress_status[AiDataEnum.PROCESSED] + 1)
            )
            if self.progress_status[AiDataEnum.PROCESSED] >= self.progress_status[AiDataEnum.TOTAL]:
                self.progress_update(AiDataEnum.CLUSTER, AiDataEnum.STATUS, AiDataEnum.COMPLETED)

    def __cluster_requirements_by_description(
        self, requirements: dict, stop_event_cluster: Event, threshold: float
    ) -> (set, dict[list[list[float]], dict]):
        clusters = []
        seen = set()
        logging.debug(self.progress_status)
        self.progress_update(AiDataEnum.CLUSTER, AiDataEnum.STATUS, AiDataEnum.CLUSTERING)

        req_ids = list(requirements.keys())
        req_id_to_index = {req_id: idx for idx, req_id in enumerate(req_ids)}
        cluster_matrix = [[0.0 for _ in range(len(req_ids))] for _ in range(len(req_ids))]

        for req_id_outer, requirement1 in requirements.items():
            req1 = requirement1.to_dict()
            if debug_enabled:
                logging.debug(req1)

            if req1["id"] in seen:
                self.__update_progress()
                continue

            cluster = {req1["id"]}
            seen.add(req1["id"])

            for req_id_inner, requirement2 in requirements.items():
                req2 = requirement2.to_dict()
                if req_id_outer != req_id_inner and req2["id"] not in seen:
                    similarity_bool, similarity_float = self.function(req1["desc"], req2["desc"], threshold)
                    cluster_matrix[req_id_to_index[req_id_outer]][req_id_to_index[req_id_inner]] = similarity_float
                    cluster_matrix[req_id_to_index[req_id_inner]][req_id_to_index[req_id_outer]] = similarity_float

                    if similarity_bool:
                        cluster.add(req2["id"])
                        seen.add(req2["id"])
                if stop_event_cluster.is_set():
                    logging.warning("CLUSTERING TERMINATED")
                    return set(), None

            clusters.append(cluster)
            self.__update_progress()
            if debug_enabled:
                logging.debug("cluster: " + req1["id"])
            if stop_event_cluster.is_set():
                logging.warning("CLUSTERING TERMINATED")
                return set(), None
        if stop_event_cluster.is_set():
            logging.warning("CLUSTERING TERMINATED")
            return set(), None
        return set(frozenset(cluster) for cluster in clusters), {"matrix": cluster_matrix, "indexing": req_id_to_index}
