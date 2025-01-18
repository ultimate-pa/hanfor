from hanfor.ai.strategies.similarity_abstract_class import SimilarityAlgorithm


class LevenshteinSimilarity(SimilarityAlgorithm):
    @property
    def standard_threshold(self) -> float:
        return 0.5

    @property
    def name(self) -> str:
        return "Levenshtein"

    @property
    def description(self) -> str:
        return "Calculates the similarity of strings based on the Levenshtein distance."

    @property
    def threshold_interval(self) -> (float, float):
        return 0.0, 1.0

    def compare(self, str1: str, str2: str, threshold: float) -> (bool, float):
        len_str1, len_str2 = len(str1), len(str2)
        dp = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

        for i in range(len_str1 + 1):
            dp[i][0] = i
        for j in range(len_str2 + 1):
            dp[0][j] = j

        for i in range(1, len_str1 + 1):
            for j in range(1, len_str2 + 1):
                cost = 0 if str1[i - 1] == str2[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

        max_len = max(len(str1), len(str2))
        similarity = 1 - (dp[len_str1][len_str2] / max_len)
        return similarity >= threshold, similarity
