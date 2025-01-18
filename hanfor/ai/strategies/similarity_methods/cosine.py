from hanfor.ai.strategies.similarity_abstract_class import SimilarityAlgorithm
import math


class LevenshteinSimilarity(SimilarityAlgorithm):
    @property
    def standard_threshold(self) -> float:
        return 0.5

    @property
    def name(self) -> str:
        return "Cosine Similarity"

    @property
    def description(self) -> str:
        return "Calculates the cosine similarity between two texts. Higher values indicate greater similarity."

    @property
    def threshold_interval(self) -> (float, float):
        return 0, 1

    def compare(self, str1: str, str2: str, threshold: float) -> (bool, float):
        words1 = str1.split()
        words2 = str2.split()

        intersection = set(words1) & set(words2)
        numerator = len(intersection)

        denominator = math.sqrt(len(words1) * len(words2))

        if denominator == 0:
            return False, 0
        similarity = numerator / denominator
        return similarity >= threshold, similarity
