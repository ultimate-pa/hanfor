import threading
from hanfor.ai import Progress
from typing import Optional
from hanfor.ai.interfaces.similarity_interface import ClusteringProgress
import reqtransformer
import hanfor_flask


class AiCore:
    clustering_progress = None
    clustering_progress_thread = None
    clusters: Optional[set[frozenset[str]]] = None
    progress_status = {
        Progress.CLUSTER: {Progress.STATUS: Progress.NOT_STARTED, Progress.PROCESSED: 0, Progress.TOTAL: 0},
        Progress.AI: {},
    }
    stop_event_cluster = threading.Event()

    def __init__(self) -> None:
        pass

    def terminate_cluster_thread(self):
        self.stop_event_cluster.set()
        self.clustering_progress_thread.join()
        self.stop_event_cluster.clear()
        self.progress_status[Progress.CLUSTER][Progress.PROCESSED] = 0
        self.progress_status[Progress.CLUSTER][Progress.STATUS] = Progress.NOT_STARTED

    def start_clustering(self) -> None:
        # If currently clustering, terminate the Thread
        if self.clustering_progress_thread and self.clustering_progress_thread.is_alive():
            self.terminate_cluster_thread()

        self.progress_status[Progress.CLUSTER][Progress.STATUS] = Progress.PENDING
        requirements = hanfor_flask.current_app.db.get_objects(reqtransformer.Requirement)
        self.progress_status[Progress.CLUSTER][Progress.TOTAL] = len(requirements)

        clustering_progress = ClusteringProgress(requirements, self.progress_status[Progress.CLUSTER])

        def clustering_thread(clustering_progress_class: ClusteringProgress, stop_event_cluster) -> None:
            self.clusters = clustering_progress_class.start(stop_event_cluster)

        self.clustering_progress_thread = threading.Thread(
            target=clustering_thread, args=(clustering_progress, self.stop_event_cluster), daemon=True
        )
        self.clustering_progress_thread.start()

    def get_info(self):
        return {
            "status": self.progress_status[Progress.CLUSTER][Progress.STATUS].value,
            "processed": self.progress_status[Progress.CLUSTER][Progress.PROCESSED],
            "total": self.progress_status[Progress.CLUSTER][Progress.TOTAL],
        }

    def get_clusters(self) -> set[frozenset[str]]:
        return self.clusters
