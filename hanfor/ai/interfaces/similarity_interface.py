import logging
from asyncio import Event
from hanfor.ai import AiDataEnum


# Enable or disable debug logging
debug_enabled = False


class ClusteringProgress:
    def __init__(self, requirements: dict, progress_status: dict, progress_update, sim_function):
        self.progress_status = progress_status
        self.progress_update = progress_update
        self.requirements = requirements
        self.function = sim_function

    def start(self, stop_event_cluster: Event) -> set:
        return self.__cluster_requirements_by_description(self.requirements, stop_event_cluster)

    def __update_progress(self):

        if self.progress_status[AiDataEnum.STATUS] == AiDataEnum.CLUSTERING:
            self.progress_update(
                AiDataEnum.CLUSTER, AiDataEnum.PROCESSED, (self.progress_status[AiDataEnum.PROCESSED] + 1)
            )
            if self.progress_status[AiDataEnum.PROCESSED] >= self.progress_status[AiDataEnum.TOTAL]:
                self.progress_update(AiDataEnum.CLUSTER, AiDataEnum.STATUS, AiDataEnum.COMPLETED)

    def __cluster_requirements_by_description(
        self,
        requirements: dict,
        stop_event_cluster: Event,
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
                    similarity_bool, similarity_float = self.function(req1["desc"], req2["desc"])

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
