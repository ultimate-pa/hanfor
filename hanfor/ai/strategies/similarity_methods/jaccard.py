import time

from hanfor.ai.strategies.similarity_abstract_class import SimilarityAlgorithm


class LevenshteinSimilarity(SimilarityAlgorithm):
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

    def compare(self, str1: str, str2: str, threshold: float) -> (bool, float):
        time.sleep(0.01)
        words1 = set(str1.split())
        words2 = set(str2.split())

        intersection = words1 & words2
        union = words1 | words2

        similarity = len(intersection) / len(union) if len(union) > 0 else 0.0
        return similarity >= threshold, similarity
