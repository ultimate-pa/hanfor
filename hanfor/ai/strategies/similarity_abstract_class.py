from abc import ABC, abstractmethod
from threading import Event
from typing import Tuple
from ai.ai_enum import AiDataEnum


class SimilarityAlgorithm(ABC):

    def __init__(self):
        self.__update_progress_function = None
        self.cluster_matrix: list[list[float]] = []
        self.req_id_to_index: dict = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the similarity algorithm (visible in Hanfor)"""
        pass

    @property
    @abstractmethod
    def standard_threshold(self) -> float:
        """Standard similarity threshold (visible in Hanfor)"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the similarity algorithm (visible in Hanfor)"""
        pass

    @property
    @abstractmethod
    def threshold_interval(self) -> Tuple[float, float]:
        """Threshold interval of the similarity algorithm"""
        pass

    @abstractmethod
    def is_within_threshold(self, set_threshold, calculated_threshold) -> bool:
        """Checks whether the calculated threshold value is within the acceptable range of the set threshold value. (for the conversion from matrix to cluster)"""
        pass

    @abstractmethod
    def generate_matrix(
        self,
        requirements: dict,
        update_progress: callable,
        set_value_matrix: callable,
        stop_event: Event,
    ) -> None:
        """
        Creates a similarity matrix based on the specified requirements

        - Must use `set_value_matrix` to populate the matrix
        - Must update the progress in real time using `update_progress`
        - Must be able to stop the process immediately using `stop_event
        """
        pass

    def __create_clusters(self, set_threshold, req_logger: callable):
        """Creates a cluster set from the matrix and logs it for each requirement (uses is_within_threshold)"""

        visited = set()
        clusters = set()
        index_to_req_id = {v: k for k, v in self.req_id_to_index.items()}

        for req1_idx, row in enumerate(self.cluster_matrix):
            req1 = index_to_req_id[req1_idx]

            if req1 in visited:
                continue
            f_set = set()
            f_set.add(req1)
            visited.add(req1)

            for req2_idx, similarity in enumerate(row):
                req2 = index_to_req_id.get(req2_idx)
                if req2 not in visited and self.is_within_threshold(set_threshold, similarity):
                    f_set.add(req2)
                    visited.add(req2)

            for r in f_set:
                req_logger(r, {"message": f"added {r} into cluster: {f_set}"})
            clusters.add(frozenset(f_set))

        return clusters

    def set_value_matrix(self, req1: str, req2: str, similarity_float: float):
        """Sets the similarity value between two requirements in the similarity matrix"""

        self.cluster_matrix[self.req_id_to_index[req1]][self.req_id_to_index[req2]] = similarity_float
        self.cluster_matrix[self.req_id_to_index[req2]][self.req_id_to_index[req1]] = similarity_float

    def update_progress(self, total: int, current: int) -> None:
        """Updates the progress for the webinterface"""

        self.__update_progress_function(AiDataEnum.CLUSTER, AiDataEnum.PROCESSED, current)
        self.__update_progress_function(AiDataEnum.CLUSTER, AiDataEnum.TOTAL, total)

    def get_clusters_and_similarity_matrix(
        self, requirements, threshold: float, stop_event: Event, update_progress: callable, req_logger: callable
    ):
        """Main method to generate clusters and the similarity matrix from requirements."""

        req_ids = list(requirements.keys())
        self.req_id_to_index = {req_id: idx for idx, req_id in enumerate(req_ids)}
        self.cluster_matrix = [[0.0 for _ in range(len(req_ids))] for _ in range(len(req_ids))]
        self.__update_progress_function = update_progress

        self.__update_progress_function(AiDataEnum.CLUSTER, AiDataEnum.STATUS, AiDataEnum.CLUSTERING)
        self.generate_matrix(requirements, self.update_progress, self.set_value_matrix, stop_event)
        self.__update_progress_function(AiDataEnum.CLUSTER, AiDataEnum.STATUS, AiDataEnum.COMPLETED)

        clusters = self.__create_clusters(threshold, req_logger)
        return clusters, {"matrix": self.cluster_matrix, "indexing": self.req_id_to_index}
