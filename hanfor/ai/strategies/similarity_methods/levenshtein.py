from threading import Event

from ai.strategies.similarity_abstract_class import SimilarityAlgorithm


def compare(str1: str, str2: str) -> (bool, float):
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
    return similarity


class LevenshteinSimilarity(SimilarityAlgorithm):

    def is_within_threshold(self, set_threshold, calculated_threshold) -> bool:
        return calculated_threshold >= set_threshold

    def generate_matrix(
        self,
        requirements,
        update_progress: callable,
        set_value_matrix: callable,
        stop_event: Event,
    ):
        seen = set()
        for req_id_outer, requirement1 in requirements.items():
            req1 = requirement1.to_dict()
            if req1["id"] in seen:
                self.update_progress(len(requirements.keys()), len(seen))
                continue
            seen.add(req1["id"])
            self.update_progress(len(requirements.keys()), len(seen))
            for req_id_inner, requirement2 in requirements.items():
                req2 = requirement2.to_dict()
                if req_id_outer != req_id_inner and req2["id"] not in seen:
                    similarity_float = compare(req1["desc"], req2["desc"])
                    self.update_progress(len(requirements.keys()), len(seen))
                    set_value_matrix(req1["id"], req2["id"], similarity_float)
                if stop_event.is_set():
                    return

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
