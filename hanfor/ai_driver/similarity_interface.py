# Test clustering methode
def levenshtein_distance(str1, str2):
    len_str1, len_str2 = len(str1), len(str2)
    # Initialize a matrix of size (len_str1+1) x (len_str2+1)
    dp = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

    # Initialize the first row and first column of the matrix
    for i in range(len_str1 + 1):
        dp[i][0] = i
    for j in range(len_str2 + 1):
        dp[0][j] = j

    # Fill in the matrix
    for i in range(1, len_str1 + 1):
        for j in range(1, len_str2 + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost  # Deletion  # Insertion
            )  # Substitution

    # The Levenshtein distance is in the last cell of the matrix
    return dp[len_str1][len_str2]


def cluster_requirements_by_description(requirements, threshold=0.5):
    clusters = []
    seen = set()  # A set to track already grouped requirements

    # Iterate over each requirement
    for i, req1 in enumerate(requirements):
        if req1["id"] in seen:
            continue
        # Create a new cluster with the current requirement
        cluster = {req1["id"]}
        seen.add(req1["id"])

        for j, req2 in enumerate(requirements):
            if i != j and req2["id"] not in seen:
                # Calculate the similarity of the descriptions
                distance = levenshtein_distance(req1["description"], req2["description"])
                max_len = max(len(req1["description"]), len(req2["description"]))
                similarity = 1 - (distance / max_len)

                # If the similarity is above the threshold, group them together
                if similarity >= threshold:
                    cluster.add(req2["id"])
                    seen.add(req2["id"])

        # Add the cluster to the list
        clusters.append(cluster)

    # Return the clusters as a set of frozenset
    return set(frozenset(cluster) for cluster in clusters)
