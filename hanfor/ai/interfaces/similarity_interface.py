import logging
import time
from asyncio import Event
from hanfor.ai import Progress
from hanfor.ai.strategies import similarity_methods


# Enable or disable debug logging
debug_enabled = False


class ClusteringProgress:
    def __init__(self, requirements: dict, progress_status: dict):
        self.progress_status = progress_status
        self.requirements = requirements

    def start(self, stop_event_cluster: Event) -> set:
        return self._cluster_requirements_by_description(self.requirements, self.progress_status, stop_event_cluster)

    def _update_progress(self):
        if self.progress_status[Progress.STATUS] == Progress.CLUSTERING:
            self.progress_status[Progress.PROCESSED] += 1
            if self.progress_status[Progress.PROCESSED] >= self.progress_status[Progress.TOTAL]:
                self.progress_status[Progress.STATUS] = Progress.COMPLETED

    def _cluster_requirements_by_description(
        self,
        requirements: dict,
        progress_status: dict,
        stop_event_cluster: Event,
        similarity_methode=similarity_methods.levenshtein_distance,
    ) -> set:
        threshold = 0.5
        clusters = []
        seen = set()

        progress_status[Progress.STATUS] = Progress.CLUSTERING

        for req_id_outer, requirement1 in requirements.items():
            req1 = requirement1.to_dict()
            if debug_enabled:
                logging.debug(req1)

            if req1["id"] in seen:
                self._update_progress()
                continue

            cluster = {req1["id"]}
            seen.add(req1["id"])

            for req_id_inner, requirement2 in requirements.items():
                req2 = requirement2.to_dict()
                if req_id_outer != req_id_inner and req2["id"] not in seen:

                    if similarity_methode(req1["desc"], req2["desc"], threshold):
                        cluster.add(req2["id"])
                        seen.add(req2["id"])
                if stop_event_cluster.is_set():
                    logging.warning("CLUSTERING TERMINATED")
                    return set()

            clusters.append(cluster)
            self._update_progress()
            time.sleep(0.01)
            if debug_enabled:
                logging.debug("cluster: " + req1["id"])
            if stop_event_cluster.is_set():
                logging.warning("CLUSTERING TERMINATED")
                return set()
        if stop_event_cluster.is_set():
            logging.warning("CLUSTERING TERMINATED")
            return set()
        return set(frozenset(cluster) for cluster in clusters)
