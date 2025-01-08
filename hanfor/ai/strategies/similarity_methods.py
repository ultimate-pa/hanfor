import math


def levenshtein_distance(str1: str, str2: str, threshold: float = 0.5) -> (bool, float):
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


# Cosine Similarity
def cosine_similarity(str1: str, str2: str, threshold: float = 0.1) -> (bool, float):
    words1 = str1.split()
    words2 = str2.split()

    intersection = set(words1) & set(words2)
    numerator = len(intersection)

    denominator = math.sqrt(len(words1) * len(words2))

    if denominator == 0:
        return False, 0
    similarity = numerator / denominator
    return similarity >= threshold, similarity


def jaccard_similarity(str1: str, str2: str, threshold: float = 0.5) -> (bool, float):
    words1 = set(str1.split())
    words2 = set(str2.split())

    intersection = words1 & words2
    union = words1 | words2

    similarity = len(intersection) / len(union) if len(union) > 0 else 0.0
    return similarity >= threshold, similarity


sim_methods = [
    {
        "name": "Levenshtein Distance",
        "function": levenshtein_distance,
        "description": "Calculates the similarity of strings based on the Levenshtein distance.",
    },
    {
        "name": "Cosine Similarity",
        "function": cosine_similarity,
        "description": "Calculates the cosine similarity between two texts. Higher values indicate greater similarity.",
    },
    {
        "name": "Jaccard Similarity",
        "function": jaccard_similarity,
        "description": "Calculates the Jaccard index based on the similarity of common and distinct words.",
    },
]
