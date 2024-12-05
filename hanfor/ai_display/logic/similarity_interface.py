import logging
import time

# Enable or disable debug logging
debug_enabled = False


def cluster_requirements_by_description(requirements, progress_tracker):
    threshold = 0.5

    clusters = []
    seen = set()

    for i, req1 in enumerate(requirements):
        if debug_enabled:
            logging.debug(req1)
        if req1["id"] in seen:
            progress_tracker.update_progress()
            continue

        cluster = {req1["id"]}
        seen.add(req1["id"])

        for j, req2 in enumerate(requirements):
            if i != j and req2["id"] not in seen:
                distance = levenshtein_distance(req1["description"], req2["description"])
                max_len = max(len(req1["description"]), len(req2["description"]))
                similarity = 1 - (distance / max_len)

                if similarity >= threshold:
                    cluster.add(req2["id"])
                    seen.add(req2["id"])

        clusters.append(cluster)

        # Update progress after processing each requirement
        progress_tracker.update_progress()

        # Simulate processing time
        time.sleep(0.1)
        if debug_enabled:
            logging.debug("cluster: " + req1["id"])

    return set(frozenset(cluster) for cluster in clusters)


def levenshtein_distance(str1, str2):
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

    return dp[len_str1][len_str2]


class ClusteringProgress:
    def __init__(self, total):
        self.processed = 0
        self.total = total
        self.status = "pending"

    def start(self):
        self.status = "clustering"

    def update_progress(self):
        if self.status == "clustering":
            self.processed += 1
            if self.processed >= self.total:
                self.status = "completed"

    def get_progress_state(self):
        return {
            "processed": self.processed,
            "total": self.total,
            "status": self.status,
        }
