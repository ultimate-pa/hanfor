def levenshtein_distance(str1: str, str2: str, threshold) -> bool:
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
    if similarity >= threshold:
        return True
    else:
        return False
