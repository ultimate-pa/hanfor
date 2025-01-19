import logging
from queue import Queue
from threading import Thread, Event, Lock
from typing import Optional, List, Any
from hanfor.ai import AiDataEnum
from hanfor.ai.interfaces import ai_interface
from hanfor.ai.interfaces.similarity_interface import ClusteringProgress, load_similarity_methods
from hanfor.ai.interfaces.ai_interface import AIFormalization, load_ai_prompt_parse_methods
from time import time
import reqtransformer
import hanfor_flask
import re


class AiProcessingQueue:
    max_ai_requests: int = 5

    def __init__(self, update_progress_function):
        self.current_ai_request = []
        self.current_waiting = []
        self.lock = Lock()
        self.__update_progress = update_progress_function

    def add_request(self, req_id: str) -> bool:
        with self.lock:
            if len(self.current_ai_request) < self.max_ai_requests:
                if req_id in self.current_waiting:
                    self.current_waiting.remove(req_id)
                self.current_ai_request.append(req_id)
                self.__up_prog()
                return True
            else:
                if req_id not in self.current_waiting:
                    self.current_waiting.append(req_id)
                return False

    def __up_prog(self):
        self.__update_progress(AiDataEnum.AI, AiDataEnum.QUEUED, len(self.current_waiting))
        self.__update_progress(AiDataEnum.AI, AiDataEnum.RUNNING, len(self.current_ai_request))

    def complete_request(self, req_id):
        self.current_ai_request.remove(req_id)
        self.__up_prog()

    def terminated(self, id: str):
        if id in self.current_waiting:
            self.current_waiting.remove(id)
        if id in self.current_ai_request:
            self.current_ai_request.remove(id)


class AiCore:

    clusters: Optional[set[frozenset[str]]] = None
    cluster_matrix: Optional[tuple[list[list[float]], dict]] = None
    formalization_objects: List[AIFormalization] = []

    ai_system_data = {
        AiDataEnum.FLAGS: {AiDataEnum.SYSTEM: True, AiDataEnum.AI: False},
        AiDataEnum.CLUSTER: {
            AiDataEnum.STATUS: AiDataEnum.NOT_STARTED,
            AiDataEnum.PROCESSED: 0,
            AiDataEnum.TOTAL: 0,
        },
        AiDataEnum.AI: {AiDataEnum.RUNNING: 0, AiDataEnum.QUEUED: 0, AiDataEnum.RESPONSE: "", AiDataEnum.QUERY: ""},
    }
    clustering_progress_thread: Optional[Thread] = None
    stop_event_cluster = Event()
    ai_formalization_thread: Optional[list[Thread]] = []
    stop_event_ai = Event()

    def __init__(self):
        self.similarity_methods = load_similarity_methods()
        self.activ_similarity_method = "Levenshtein"
        self.sim_threshold = self.similarity_methods["Levenshtein"].standard_threshold

        self.ai_prompt_parse_methods = load_ai_prompt_parse_methods()
        self.activ_ai_prompt_parse_methods = "Prompt Dump"
        self.used_variables: list[dict] = [{}]

        self.ai_processing_queue = AiProcessingQueue(self.__update_progress)
        self.clustering_progress = None
        self.__locked_cluster = []

    def terminate_cluster_thread(self):
        if self.clustering_progress_thread and self.clustering_progress_thread.is_alive():
            self.stop_event_cluster.set()
            self.clustering_progress_thread.join()
            self.clustering_progress = None
            self.stop_event_cluster.clear()
            self.__update_progress(AiDataEnum.CLUSTER, AiDataEnum.PROCESSED, 0)
            self.__update_progress(AiDataEnum.CLUSTER, AiDataEnum.STATUS, AiDataEnum.NOT_STARTED)

    def start_clustering(self) -> None:
        # If currently clustering, terminate the Thread
        if self.clustering_progress_thread and self.clustering_progress_thread.is_alive():
            self.terminate_cluster_thread()

        self.__update_progress(
            AiDataEnum.CLUSTER,
            None,
            {
                AiDataEnum.STATUS: AiDataEnum.PENDING,
                AiDataEnum.PROCESSED: 0,
                AiDataEnum.TOTAL: 0,
            },
        )

        requirements = hanfor_flask.current_app.db.get_objects(reqtransformer.Requirement)
        self.__update_progress(AiDataEnum.CLUSTER, AiDataEnum.TOTAL, len(requirements))
        self.clustering_progress = ClusteringProgress(
            requirements,
            self.ai_system_data[AiDataEnum.CLUSTER],
            self.__update_progress,
            self.similarity_methods[self.activ_similarity_method].compare,
        )

        def clustering_thread(clustering_progress_class: ClusteringProgress, stop_event_cluster: Event) -> None:
            self.clusters, self.cluster_matrix = clustering_progress_class.start(stop_event_cluster, self.sim_threshold)

        self.clustering_progress_thread = Thread(
            target=clustering_thread, args=(self.clustering_progress, self.stop_event_cluster), daemon=True
        )
        self.clustering_progress_thread.start()

    def terminate_ai_formalization_threads(self) -> None:
        self.stop_event_ai.set()
        for thread in self.ai_formalization_thread:
            if thread and thread.is_alive():
                thread.join()
        self.stop_event_ai.clear()

    def updated_requirement(self, rid_u: str) -> None:

        if not self.clusters or not self.__check_template_for_ai_formalization(rid_u):
            logging.debug("No Formalization")
            return

        req_queue, l_cluster = self.__load_requirements_to_queue(rid_u)
        self.__get_used_variables()
        mother_tread = Thread(
            target=self.__mother_thread_of_ai_formalization,
            args=(
                req_queue,
                hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, rid_u),
                self.stop_event_ai,
                l_cluster,
            ),
            daemon=True,
        )
        self.ai_formalization_thread.append(mother_tread)
        mother_tread.start()

    def get_full_info(self) -> dict:
        ret = {
            "cluster_status": self.__get_info_cluster_status(),
            "clusters": self.__get_clusters(),
            "ai_status": self.__get_info_ai_status(),
            "ai_formalization": self.__get_ai_formalization_progress(),
            "flags": self.__get_info_flags(),
            "sim_methods": self.__get_info_sim_methods(),
            "ai_methods": self.__get_info_ai_methods(),
        }
        return ret

    def get_matrix(self) -> tuple[list[list[float]], dict] | None:
        logging.debug(self.cluster_matrix)
        return self.cluster_matrix

    def set_sim_methode(self, name: str) -> None:
        if name in self.similarity_methods.keys():
            logging.debug(name)
            self.activ_similarity_method = name
            self.sim_threshold = self.similarity_methods[name].standard_threshold

    def set_sim_threshold(self, threshold: float) -> None:
        self.sim_threshold = threshold
        logging.debug(self.sim_threshold)

    def set_flag_system(self, flag_system: bool) -> None:
        self.__update_progress(AiDataEnum.FLAGS, AiDataEnum.SYSTEM, flag_system)

    def set_flag_ai(self, flag_ai: bool) -> None:
        self.__update_progress(AiDataEnum.FLAGS, AiDataEnum.AI, flag_ai)

    def query_ai(self, query):
        def background_query(processed_query):
            response, _ = ai_interface.query_ai(processed_query)
            self.__update_progress(AiDataEnum.AI, AiDataEnum.RESPONSE, response)

        processed_query = self.__process_query(query)
        self.__update_progress(AiDataEnum.AI, AiDataEnum.QUERY, processed_query)
        self.__update_progress(AiDataEnum.AI, AiDataEnum.RESPONSE, None)

        thread = Thread(target=background_query, args=(processed_query,), daemon=True)
        thread.start()

    def check_for_process(self):
        if self.clusters:
            for cl in self.clusters:
                for req_id in cl:
                    if self.__check_template_for_ai_formalization(req_id):
                        self.updated_requirement(req_id)

    def set_ai_methode(self, name: str) -> None:
        if name in self.ai_prompt_parse_methods.keys():
            logging.debug(name)
            self.activ_ai_prompt_parse_methods = name

    def __process_query(self, query):
        def replace_placeholder(match):
            placeholder = match.group(1)
            try:
                req_id_action = placeholder.split(".")
                if len(req_id_action) != 2:
                    return f"[Error: Invalid format for {placeholder}]"

                req_id, action = req_id_action
                req = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, req_id)

                if req:
                    req_dict = req.to_dict(include_used_vars=True)
                    if action in req_dict:
                        return str(req_dict[action])
                    else:
                        return f"[Error: Action {action} not found for req_id {req_id}]"
                else:
                    return f"[Error: req_id {req_id} not found]"
            except Exception as e:
                return f"[Error processing {placeholder}: {e}]"

        pattern = r"\[([^\[\]]+?)\]"
        return re.sub(pattern, replace_placeholder, query)

    def __get_info_flags(self) -> dict:
        return {
            "system": self.ai_system_data[AiDataEnum.FLAGS][AiDataEnum.SYSTEM],
            "ai": self.ai_system_data[AiDataEnum.FLAGS][AiDataEnum.AI],
        }

    def __get_info_ai_status(self) -> dict:
        return {
            "running": self.ai_system_data[AiDataEnum.AI][AiDataEnum.RUNNING],
            "queued": self.ai_system_data[AiDataEnum.AI][AiDataEnum.QUEUED],
            "response": self.ai_system_data[AiDataEnum.AI][AiDataEnum.RESPONSE],
            "query": self.ai_system_data[AiDataEnum.AI][AiDataEnum.QUERY],
        }

    def __update_progress(self, progress_outer: AiDataEnum, progress_inner: Optional[AiDataEnum], update):
        if progress_inner:
            self.ai_system_data[progress_outer][progress_inner] = update
        else:
            self.ai_system_data[progress_outer] = update

    def __get_info_cluster_status(self) -> dict:
        return {
            "status": self.ai_system_data[AiDataEnum.CLUSTER][AiDataEnum.STATUS].value,
            "processed": self.ai_system_data[AiDataEnum.CLUSTER][AiDataEnum.PROCESSED],
            "total": self.ai_system_data[AiDataEnum.CLUSTER][AiDataEnum.TOTAL],
        }

    def __get_clusters(self):
        if self.clusters:
            return [list(cluster) for cluster in self.clusters]
        return []

    def __get_info_sim_methods(self) -> (float, list):
        methods_info = []
        if self.similarity_methods:
            for name, method in self.similarity_methods.items():
                method_info = {
                    "name": name,
                    "description": method.description,
                    "interval": method.threshold_interval,
                    "default": method.standard_threshold,
                    "selected": name == self.activ_similarity_method,
                }
                methods_info.append(method_info)
        return self.sim_threshold, methods_info

    def __get_info_ai_methods(self) -> list:
        methods_info = []
        if self.ai_prompt_parse_methods:
            for name, method in self.ai_prompt_parse_methods.items():
                method_info = {
                    "name": name,
                    "description": method.description,
                    "selected": name == self.activ_ai_prompt_parse_methods,
                }
                methods_info.append(method_info)
        return methods_info

    def __get_ai_formalization_progress(self) -> list[dict[str, Any]]:
        self.__cleanup_old_formalizations()
        return [
            {
                "id": f_obj.req_ai.to_dict().get("id"),
                "status": f_obj.status,
                "prompt": f_obj.prompt,
                "ai_response": f_obj.ai_response,
                "formalized_output": f_obj.formalized_output,
                "try_count": f_obj.try_count,
                "time": f_obj.del_time,
            }
            for f_obj in self.formalization_objects
        ]

    def __cleanup_old_formalizations(self):
        current_time = time()
        self.formalization_objects = [
            f_obj
            for f_obj in self.formalization_objects
            if f_obj.del_time is None or (current_time - f_obj.del_time < 10)
        ]

    def __mother_thread_of_ai_formalization(
        self, req_queue: Queue, req_u: reqtransformer.Requirement, stop_event_ai: Event, l_cluster: frozenset
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
            processing_thread = Thread(target=self.__process_queue_element, args=(formalize_object,), daemon=True)
            processing_thread.start()
            threads.append(processing_thread)
        for thread in threads:
            thread.join()
        if l_cluster:
            self.__locked_cluster.remove(l_cluster)
        if stop_event_ai.is_set():
            logging.info("Terminated ai formalization")
        else:
            logging.info("Finished processing the queue.")

    @staticmethod
    def __check_template_for_ai_formalization(rid: str) -> bool:
        req = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, rid).to_dict(include_used_vars=True)
        return "has_formalization" in req["tags"]

    def __load_requirements_to_queue(self, rid: str) -> (Queue, frozenset):
        req_queue = Queue()
        l_cluster = None
        for cl in self.clusters:
            if rid in cl:
                if cl in self.__locked_cluster:
                    logging.info(f"Cluster {cl} is already locked, stopping the process.")
                    return req_queue, l_cluster
                self.__locked_cluster.append(cl)
                l_cluster = cl
                for req_id in cl:
                    requirement = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, req_id)
                    if self.__check_ai_should_formalized(requirement):
                        req_queue.put(requirement)
                break
        return req_queue, l_cluster

    @staticmethod
    def __check_ai_should_formalized(requirement: reqtransformer.Requirement) -> bool:
        return not requirement.to_dict(include_used_vars=True)["formal"]

    @staticmethod
    def __formalization_integration(formalization: dict, requirement: reqtransformer.Requirement) -> None:

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
                "tags": dumps({"ai_formalization": "AI-generated formalization based on human-created formalization"}),
                "status": "Todo",
                "formalizations": formatted_output_json,
            },
        )

    def __get_used_variables(self):
        """Return list of used variables from the database with Typ, etc"""
        self.used_variables = [
            x.to_dict({}) for x in hanfor_flask.current_app.db.get_objects(reqtransformer.Variable).values()
        ]

    def __process_queue_element(self, formalize_object: AIFormalization) -> None:
        formalize_object.run_process(
            self.ai_processing_queue,
            self.ai_prompt_parse_methods[self.activ_ai_prompt_parse_methods].create_prompt,
            self.ai_prompt_parse_methods[self.activ_ai_prompt_parse_methods].parse_ai_response,
            self.used_variables,
        )
        if self.stop_event_ai.is_set() or formalize_object.status.startswith("terminated"):
            logging.warning(formalize_object.status)
            return
        if formalize_object.status == "complete":
            self.__formalization_integration(formalize_object.formalized_output, formalize_object.req_ai)
