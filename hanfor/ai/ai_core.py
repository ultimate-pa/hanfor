import logging
from queue import Queue
from threading import Thread, Event
from typing import Optional, List, Any
from hanfor.ai import Progress
from hanfor.ai.interfaces.similarity_interface import ClusteringProgress
from hanfor.ai.interfaces.ai_interface import AIFormalization
from time import time
import reqtransformer
import hanfor_flask


class AiCore:

    clusters: Optional[set[frozenset[str]]] = None
    formalization_objects: List[AIFormalization] = []

    progress_status = {
        Progress.CLUSTER: {Progress.STATUS: Progress.NOT_STARTED, Progress.PROCESSED: 0, Progress.TOTAL: 0},
        Progress.AI: {},
    }

    clustering_progress_thread: Optional[Thread] = None
    stop_event_cluster = Event()

    ai_formalization_thread: Optional[Thread] = None
    stop_event_ai = Event()

    def __init__(self):
        self.clustering_progress = None
        self._locked_cluster = []

    def _update_progress(self, progress_outer: Progress, progress_inner: Optional[Progress], update):
        if progress_inner:
            self.progress_status[progress_outer][progress_inner] = update
        else:
            self.progress_status[progress_outer] = update

    def terminate_cluster_thread(self):
        if self.clustering_progress_thread and self.clustering_progress_thread.is_alive():
            self.stop_event_cluster.set()
            self.clustering_progress_thread.join()
            self.clustering_progress = None
            self.stop_event_cluster.clear()
            self._update_progress(Progress.CLUSTER, Progress.PROCESSED, 0)
            self._update_progress(Progress.CLUSTER, Progress.STATUS, Progress.NOT_STARTED)

    def start_clustering(self) -> None:
        # If currently clustering, terminate the Thread
        if self.clustering_progress_thread and self.clustering_progress_thread.is_alive():
            self.terminate_cluster_thread()

        self._update_progress(
            Progress.CLUSTER,
            None,
            {
                Progress.STATUS: Progress.PENDING,
                Progress.PROCESSED: 0,
                Progress.TOTAL: 0,
            },
        )

        requirements = hanfor_flask.current_app.db.get_objects(reqtransformer.Requirement)
        self._update_progress(Progress.CLUSTER, Progress.TOTAL, len(requirements))

        self.clustering_progress = ClusteringProgress(
            requirements, self.progress_status[Progress.CLUSTER], self._update_progress
        )

        def clustering_thread(clustering_progress_class: ClusteringProgress, stop_event_cluster: Event) -> None:
            self.clusters = clustering_progress_class.start(stop_event_cluster)

        self.clustering_progress_thread = Thread(
            target=clustering_thread, args=(self.clustering_progress, self.stop_event_cluster), daemon=True
        )
        self.clustering_progress_thread.start()

    def terminate_ai_formalization_threads(self) -> None:
        if self.ai_formalization_thread and self.ai_formalization_thread.is_alive():
            self.stop_event_ai.set()
            self.ai_formalization_thread.join()
            self.stop_event_ai.clear()

    def updated_requirement(self, rid_u: str) -> None:
        if not self.clusters or not self._check_template_for_ai_formalization(rid_u):
            logging.debug("No Formalization")
            return
        req_queue = self._load_requirements_to_queue(rid_u)
        self.ai_formalization_thread = Thread(
            target=self._mother_thread_of_ai_formalization,
            args=(
                req_queue,
                hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, rid_u),
                self.stop_event_ai,
            ),
            daemon=True,
        )
        self.ai_formalization_thread.start()

    def get_info(self) -> dict:
        return {
            "status": self.progress_status[Progress.CLUSTER][Progress.STATUS].value,
            "processed": self.progress_status[Progress.CLUSTER][Progress.PROCESSED],
            "total": self.progress_status[Progress.CLUSTER][Progress.TOTAL],
        }

    def get_clusters(self) -> set[frozenset[str]]:
        return self.clusters

    def get_ai_formalization_progress(self) -> list[dict[str, Any]]:
        self._cleanup_old_formalizations()
        return [
            {
                "id": f_obj.req_ai.to_dict().get("id"),
                "status": f_obj.status,
                "prompt": f_obj.prompt,
                "ai_response": f_obj.ai_response,
                "formalized_output": f_obj.formalized_output,
                "time": f_obj.del_time,
            }
            for f_obj in self.formalization_objects
        ]

    def _cleanup_old_formalizations(self):
        current_time = time()
        self.formalization_objects = [
            f_obj
            for f_obj in self.formalization_objects
            if f_obj.del_time is None or (current_time - f_obj.del_time < 10)
        ]

    def _mother_thread_of_ai_formalization(
        self, req_queue: Queue, req_u: reqtransformer.Requirement, stop_event_ai: Event
    ) -> None:
        threads = []
        logging.debug("mother_thread")
        while not req_queue.empty():
            if stop_event_ai.is_set():
                break
            requirement = req_queue.get()
            formalize_object = AIFormalization(requirement, req_u, stop_event_ai)
            self.formalization_objects.append(formalize_object)
            logging.debug(requirement.to_dict())
            processing_thread = Thread(target=self._process_queue_element, args=(formalize_object,), daemon=True)
            processing_thread.start()
            threads.append(processing_thread)
        for thread in threads:
            thread.join()
        if stop_event_ai.is_set():
            logging.info("Terminated ai formalization")
        else:
            logging.info("Finished processing the queue.")

    @staticmethod
    def _check_template_for_ai_formalization(rid: str) -> bool:
        req = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, rid).to_dict(include_used_vars=True)
        return "has_formalization" in req["tags"]

    def _load_requirements_to_queue(self, rid: str) -> Queue:
        req_queue = Queue()
        for cl in self.clusters:
            if rid in cl:
                if cl in self._locked_cluster:
                    logging.info(f"Cluster {cl} is already locked, stopping the process.")
                    return req_queue
                self._locked_cluster.append(cl)
                for req_id in cl:
                    requirement = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, req_id)
                    if self._check_ai_should_formalized(requirement):
                        req_queue.put(requirement)
        return req_queue

    @staticmethod
    def _check_ai_should_formalized(requirement: reqtransformer.Requirement) -> bool:
        return not requirement.to_dict(include_used_vars=True)["formal"]

    @staticmethod
    def _formalization_integration(formalization: dict, requirement: reqtransformer.Requirement) -> None:

        formalization_id, _ = requirement.add_empty_formalization()

        # as long as current_app is not working in multithread

        from requests import post
        from json import dumps

        formatted_output_json = dumps(
            {
                str(formalization_id): {
                    "id": str(formalization_id),
                    "scope": formalization["scope"],
                    "pattern": formalization["pattern"],
                    "expression_mapping": formalization["expression_mapping"],
                }
            }
        )
        post(
            "http://127.0.0.1:5000/api/req/" + "update",
            data={
                "id": requirement.to_dict(include_used_vars=True)["id"],
                "row_idx": "2",
                "update_formalization": "true",
                "tags": "{}",
                "status": "Todo",
                "formalizations": formatted_output_json,
            },
        )

    def _process_queue_element(self, formalize_object: AIFormalization) -> None:
        formalize_object.run_process()
        if self.stop_event_ai.is_set():
            return
        self._formalization_integration(formalize_object.formalized_output, formalize_object.req_ai)
