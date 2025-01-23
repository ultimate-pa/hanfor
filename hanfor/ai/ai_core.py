import logging
from queue import Queue
from threading import Thread, Event
from typing import Optional
from ai.strategies import ai_prompt_parse_abstract_class
from ai.strategies.similarity_abstract_class import SimilarityAlgorithm
from ai import ai_config
from ai.ai_enum import AiDataEnum
from ai.ai_utils import AiStatistic, AiProcessingQueue, AiData
from ai.interfaces import ai_interface
from ai.interfaces.ai_interface import AIFormalization
import reqtransformer
import hanfor_flask
import re


class AiCore:

    def __init__(self):
        self.clustering_progress_thread: Optional[Thread] = None
        self.stop_event_cluster = Event()
        self.sim_class = None
        self.__locked_cluster = []

        self.ai_formalization_thread: Optional[list[Thread]] = []
        self.stop_event_ai = Event()

        self.ai_statistic = AiStatistic()
        self.__ai_data: AiData = AiData(self.ai_statistic)
        self.ai_processing_queue = AiProcessingQueue(self.__ai_data.update_progress)

    def startup(self):
        if ai_config.ENABLE_SIMILARITY_ON_STARTUP:
            self.start_clustering()

    def terminate_cluster_thread(self) -> None:
        if self.clustering_progress_thread and self.clustering_progress_thread.is_alive():
            self.stop_event_cluster.set()
            self.clustering_progress_thread.join()
            self.sim_class = None
            self.stop_event_cluster.clear()
            self.__ai_data.update_progress(AiDataEnum.CLUSTER, AiDataEnum.PROCESSED, 0)
            self.__ai_data.update_progress(AiDataEnum.CLUSTER, AiDataEnum.STATUS, AiDataEnum.NOT_STARTED)

    def terminate_ai_formalization_threads(self) -> None:
        self.stop_event_ai.set()
        for thread in self.ai_formalization_thread:
            if thread and thread.is_alive():
                thread.join()
        self.stop_event_ai.clear()

    def start_clustering(self) -> None:
        # If currently clustering, terminate the Thread
        if self.clustering_progress_thread and self.clustering_progress_thread.is_alive():
            self.terminate_cluster_thread()

        self.__ai_data.update_progress(
            AiDataEnum.CLUSTER,
            None,
            {
                AiDataEnum.STATUS: AiDataEnum.PENDING,
                AiDataEnum.PROCESSED: 0,
                AiDataEnum.TOTAL: 0,
            },
        )
        requirements = hanfor_flask.current_app.db.get_objects(reqtransformer.Requirement)
        self.sim_class = self.__ai_data.get_sim_class()

        def clustering_thread(sim_class: SimilarityAlgorithm, stop_event_cluster: Event) -> None:
            clusters, matrix = sim_class.get_clusters_and_similarity_matrix(
                requirements, self.__ai_data.get_sim_threshold(), stop_event_cluster, self.__ai_data.update_progress
            )
            self.__ai_data.set_clusters(clusters)
            self.__ai_data.set_cluster_matrix(matrix)

        self.clustering_progress_thread = Thread(
            target=clustering_thread, args=(self.sim_class, self.stop_event_cluster), daemon=True
        )
        self.clustering_progress_thread.start()

    def auto_update_requirement(self, rid_u: str) -> None:
        if not self.__ai_data.get_flags()[AiDataEnum.SYSTEM]:
            logging.debug("Auto update off")
            return
        self.__update_requirement(rid_u)

    def __update_requirement(self, rid_u: str) -> None:

        if not self.__ai_data.get_clusters() or not check_template_for_ai_formalization(rid_u):
            logging.debug("No Formalization")
            return

        req_queue, l_cluster = self.__load_requirements_to_queue(rid_u)
        self.__update_used_variables()
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
        return self.__ai_data.get_full_info()

    def get_matrix(self) -> tuple[list[list[float]], dict] | None:
        return self.__ai_data.get_cluster_matrix()

    def set_sim_methode(self, name: str) -> None:
        self.__ai_data.set_sim_methode(name)

    def set_sim_threshold(self, threshold: float) -> None:
        self.__ai_data.set_sim_threshold(threshold)

    def set_flag_system(self, flag_system: bool) -> None:
        self.__ai_data.update_progress(AiDataEnum.FLAGS, AiDataEnum.SYSTEM, flag_system)

    def set_flag_ai(self, flag_ai: bool) -> None:
        self.__ai_data.update_progress(AiDataEnum.FLAGS, AiDataEnum.AI, flag_ai)

    def query_ai(self, query):
        def background_query(processed_query):
            response, status = ai_interface.query_ai(
                processed_query,
                self.__ai_data.get_activ_ai_model(),
                self.__ai_data.get_flags()[AiDataEnum.AI],
            )
            if not response:
                self.__ai_data.update_progress(AiDataEnum.AI, AiDataEnum.RESPONSE, status)
            else:
                self.__ai_data.update_progress(AiDataEnum.AI, AiDataEnum.RESPONSE, response)

        processed_query = self.process_query(query)
        self.__ai_data.update_progress(AiDataEnum.AI, AiDataEnum.QUERY, processed_query)
        self.__ai_data.update_progress(AiDataEnum.AI, AiDataEnum.RESPONSE, None)

        thread = Thread(target=background_query, args=(processed_query,), daemon=True)
        thread.start()

    def check_for_process(self):
        for cl in self.__ai_data.get_clusters():
            for req_id in cl:
                logging.debug(f"Checking {req_id}")
                if check_template_for_ai_formalization(req_id):
                    self.__update_requirement(req_id)

    def set_ai_methode(self, name: str) -> None:
        self.__ai_data.set_ai_methode(name)

    def set_ai_model(self, name: str) -> None:
        self.__ai_data.set_ai_model(name)

    def __load_requirements_to_queue(self, rid: str) -> (Queue, frozenset):
        req_queue = Queue()
        l_cluster = None
        for cl in self.__ai_data.get_clusters():
            if rid in cl:
                if cl in self.__locked_cluster:
                    logging.info(f"Cluster {cl} is already locked, stopping the process.")
                    return req_queue, l_cluster
                self.__locked_cluster.append(cl)
                l_cluster = cl
                for req_id in cl:
                    requirement = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, req_id)
                    if check_ai_should_formalized(requirement):
                        req_queue.put(requirement)
                break
        return req_queue, l_cluster

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
            self.__ai_data.add_formalization_object(formalize_object)
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

    def __update_used_variables(self):
        """Return list of used variables from the database with Typ, etc"""
        self.__ai_data.set_used_variables(
            [x.to_dict({}) for x in hanfor_flask.current_app.db.get_objects(reqtransformer.Variable).values()]
        )

    def __process_queue_element(self, formalize_object: AIFormalization) -> None:
        formalize_object.run_process(
            self.ai_processing_queue,
            self.__ai_data.get_activ_ai_method_object().create_prompt,
            self.__ai_data.get_activ_ai_method_object().parse_ai_response,
            self.__ai_data.get_used_variables(),
            self.__ai_data.get_activ_ai_model(),
            self.__ai_data.get_flags()[AiDataEnum.AI],
            self.ai_statistic,
            self.__ai_data.get_activ_ai_method_object().name,
        )
        if self.stop_event_ai.is_set() or formalize_object.status.startswith("terminated"):
            logging.warning(formalize_object.status)
            return
        if formalize_object.status == "complete":
            formalization_integration(formalize_object.formalized_output, formalize_object.req_ai)

    def process_query(self, query):
        def replace_placeholder(match):
            placeholder = match.group(1)
            try:
                if placeholder == "variables":
                    self.__update_used_variables()
                    var_str = ""
                    for var in self.__ai_data.get_used_variables():
                        var_str += f"{var["name"]}: {var["type"]}, "
                    return var_str[:-2]
                if placeholder == "patterns":
                    patterns_str = ""
                    for key, value in ai_prompt_parse_abstract_class.get_pattern().items():
                        patterns_str += (
                            key
                            + ": "
                            + str(value["pattern"])
                            + (f" (usable typs: {value["env"]})" if "env" in value else "")
                            + "\n"
                        )
                    return patterns_str
                if placeholder == "scopes":
                    scopes_str = ""
                    for key, value in ai_prompt_parse_abstract_class.get_scope().items():
                        scopes_str += key + ": " + value + "\n"
                    return scopes_str
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


def check_template_for_ai_formalization(rid: str) -> bool:
    req = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, rid).to_dict(include_used_vars=True)
    return "has_formalization" in req["tags"]


def check_ai_should_formalized(requirement: reqtransformer.Requirement) -> bool:
    return not requirement.to_dict(include_used_vars=True)["formal"]


# TODO (Waiting for requirement.update_formalization not needing the app (out of context area) meanwhile through API)
def formalization_integration(formalization: dict, requirement: reqtransformer.Requirement) -> None:

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
