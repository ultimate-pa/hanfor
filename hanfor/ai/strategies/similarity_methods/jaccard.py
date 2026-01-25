from threading import Event
from ai.strategies.similarity_abstract_class import SimilarityAlgorithm


def compare(str1: str, str2: str) -> (bool, float):
    words1 = set(str1.split())
    words2 = set(str2.split())

    intersection = words1 & words2
    union = words1 | words2

    similarity = len(intersection) / len(union) if len(union) > 0 else 0.0
    return similarity


class JaccardSimilarity(SimilarityAlgorithm):
    def is_within_threshold(self, set_threshold, calculated_threshold) -> bool:
        return calculated_threshold >= set_threshold

    def generate_matrix(
        self, requirements: dict, update_progress: callable, set_value_matrix: callable, stop_event: Event
    ):
        seen = set()
        for req_id_outer, requirement1 in requirements.items():
            req1 = requirement1.to_dict()
            if req1["id"] in seen:
                continue
            seen.add(req1["id"])
            for req_id_inner, requirement2 in requirements.items():
                req2 = requirement2.to_dict()
                if req_id_outer != req_id_inner and req2["id"] not in seen:
                    similarity_float = compare(req1["desc"], req2["desc"])
                    set_value_matrix(req1["id"], req2["id"], similarity_float)
                if stop_event.is_set():
                    return
            self.update_progress(len(requirements.keys()), len(seen))

    @property
    def standard_threshold(self) -> float:
        return 0.7

    @property
    def name(self) -> str:
        return "Jaccard Similarity"

    @property
    def description(self) -> str:
        return "Calculates the Jaccard index based on the similarity of common and distinct words."

    @property
    def threshold_interval(self) -> (float, float):
        return 0.0, 1.0
