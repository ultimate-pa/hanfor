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
from json_db_connector.json_db import DatabaseKeyError


class AiCore:
    """Main class for handling all Ai related tasks"""

    def __init__(self):
        self.clustering_progress_thread: Optional[Thread] = None
        self.stop_event_cluster = Event()
        self.sim_class = None
        self.__locked_cluster = []
        self.__locked_ids = []

        self.ai_formalization_thread: Optional[list[Thread]] = []
        self.stop_event_ai = Event()

        self.ai_statistic = AiStatistic()
        self.__ai_data: AiData = AiData(self.ai_statistic)
        self.ai_processing_queue = AiProcessingQueue(self.__ai_data.update_progress)

    def startup(self, data_folder: str) -> None:
        """
        Optionally starts the clustering process and sets the data folder for logging.
        This method is executed at the end of `startup_hanfor`.
        """

        self.__ai_data.set_data_folder(data_folder)
        if ai_config.ENABLE_SIMILARITY_ON_STARTUP:
            self.start_clustering()
        id_list = []
        for requirement in hanfor_flask.current_app.db.get_objects(reqtransformer.Requirement).values():
            id_list.append(requirement.to_dict()["id"])
        self.__ai_data.requirement_log.set_ids(id_list)

    def start_clustering(self) -> None:
        """Initiates the clustering process thread for requirements using the defined similarity algorithm"""

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
                requirements,
                self.__ai_data.get_sim_threshold(),
                stop_event_cluster,
                self.__ai_data.update_progress,
                self.__ai_data.requirement_log.add_data,
            )
            self.__ai_data.set_clusters(clusters)
            self.__ai_data.set_cluster_matrix(matrix)

        self.clustering_progress_thread = Thread(
            target=clustering_thread, args=(self.sim_class, self.stop_event_cluster), daemon=True
        )
        self.clustering_progress_thread.start()

    # region Automatic AI-Based Requirement Processing

    def auto_update_requirement(self, rid_u: str) -> None:
        """Helper method to check if the system flag for auto-updating is enabled"""

        if not self.__ai_data.get_flags()[AiDataEnum.SYSTEM]:
            logging.debug("Auto update off")
            return
        self.__update_requirement(rid_u)

    def __update_requirement(self, rid_u: str) -> None:
        """
        Creates a thread to process requirements within the same cluster as the provided requirement,
        if a certain validation test is passed.
        """

        req_u = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, rid_u)
        if not self.__ai_data.get_clusters() or not check_template_for_ai_formalization(req_u):
            logging.debug("No Formalization")
            return

        req_queue, l_cluster, requirement_with_formalization = self.__load_requirements_to_queue(rid_u)
        self.__update_used_variables()
        mother_tread = Thread(
            target=self.__mother_thread_of_ai_formalization,
            args=(
                req_queue,
                requirement_with_formalization,
                self.stop_event_ai,
                l_cluster,
            ),
            daemon=True,
        )
        self.ai_formalization_thread.append(mother_tread)
        mother_tread.start()

    # endregion

    # region Terminating Methods (for all Ai threads or the clustering process)

    def terminate_cluster_thread(self) -> None:
        """Terminates the clustering thread if it is running and resets related states"""
        if self.clustering_progress_thread and self.clustering_progress_thread.is_alive():
            self.stop_event_cluster.set()
            self.clustering_progress_thread.join()
            self.sim_class = None
            self.stop_event_cluster.clear()
            self.__ai_data.update_progress(AiDataEnum.CLUSTER, AiDataEnum.PROCESSED, 0)
            self.__ai_data.update_progress(AiDataEnum.CLUSTER, AiDataEnum.STATUS, AiDataEnum.NOT_STARTED)
            self.__ai_data.set_clusters(None)
            self.__ai_data.set_cluster_matrix(None)

    def terminate_ai_formalization_threads(self) -> None:
        """Terminates all active Ai formalization threads"""
        self.stop_event_ai.set()
        for thread in self.ai_formalization_thread:
            if thread and thread.is_alive():
                thread.join()
        self.stop_event_ai.clear()

    # endregion

    # region Methods for certain applications only used from the web interface (API)

    def update_and_process_sertan_requirements(self, req_list: str) -> Optional[DatabaseKeyError]:
        """Updates and processes requirements for AI formalization from a given list of IDs."""

        req_queue = Queue()
        requirement_with_formalization = []
        l_cluster = set()

        for req in map(str.strip, req_list.split(",")):
            if req:
                l_cluster.add(req)

        for req_id in l_cluster:
            try:
                requirement = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, req_id)
            except DatabaseKeyError as e:
                return e
            if check_template_for_ai_formalization(requirement):
                requirement_with_formalization.append(requirement)
                continue

            if check_ai_should_formalized(requirement):
                if req_id in self.__locked_ids:
                    continue
                self.__locked_ids.append(req_id)
                req_queue.put(requirement)

        logging.debug(f"{l_cluster} locked")
        logging.debug(f"Queue content: {[item for item in list(req_queue.queue)]} req_queue")
        logging.debug(f"{requirement_with_formalization} requirement_with_formalization")

        self.__update_used_variables()
        mother_tread = Thread(
            target=self.__mother_thread_of_ai_formalization,
            args=(
                req_queue,
                requirement_with_formalization,
                self.stop_event_ai,
                l_cluster,
            ),
            daemon=True,
        )
        self.ai_formalization_thread.append(mother_tread)
        mother_tread.start()

    def check_all_clusters_for_need_of_ai_formalisation(self):
        """Checks all clustered requirements and updates those needing AI formalization"""

        for cl in self.__ai_data.get_clusters():
            for req_id in cl:
                logging.debug(f"Checking {req_id}")
                req = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, req_id)
                if check_template_for_ai_formalization(req):
                    self.__update_requirement(req_id)

    # endregion

    # region Custom Ai query methods

    def query_ai(self, unprocessed_query: str) -> None:
        """Processes and sends a query to the AI model asynchronously"""

        def ai_query_thread(query):
            response, status = ai_interface.query_ai(
                query,
                self.__ai_data.get_activ_ai_model(),
                self.__ai_data.get_flags()[AiDataEnum.AI],
            )
            if not response:
                self.__ai_data.update_progress(AiDataEnum.AI, AiDataEnum.RESPONSE, status)
            else:
                self.__ai_data.update_progress(AiDataEnum.AI, AiDataEnum.RESPONSE, response)

        processed_query = self.__process_query(unprocessed_query)
        self.__ai_data.update_progress(AiDataEnum.AI, AiDataEnum.QUERY, processed_query)
        self.__ai_data.update_progress(AiDataEnum.AI, AiDataEnum.RESPONSE, None)

        thread = Thread(target=ai_query_thread, args=(processed_query,), daemon=True)
        thread.start()

    def __process_query(self, query: str) -> str:
        """Processes a query string by replacing placeholders with corresponding values"""

        def replace_placeholder(match):
            placeholder = match.group(1)
            try:
                if placeholder == "variables":
                    self.__update_used_variables()
                    var_str = ""
                    for var in self.__ai_data.get_used_variables():
                        var_str += f"{var["name"]}: {var["type"]}, "
                    return var_str[:-2]
                if placeholder == "scopes":
                    scopes_str = ""
                    for key, value in ai_prompt_parse_abstract_class.get_scope().items():
                        scopes_str += key + ": " + value + "\n"
                    return scopes_str
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

                req_id_action = placeholder.split(".")
                if len(req_id_action) != 2:
                    return f"[Error: Invalid format for {placeholder}]"

                if req_id_action[0] == "pattern":
                    patterns = ai_prompt_parse_abstract_class.get_pattern()
                    if req_id_action[1] in patterns.keys():
                        return (
                            req_id_action[1]
                            + ": "
                            + str(patterns[req_id_action[1]]["pattern"])
                            + (
                                f" (usable typs: {patterns[req_id_action[1]]["env"]})"
                                if "env" in patterns[req_id_action[1]]
                                else ""
                            )
                            + "\n"
                        )
                    else:
                        return f"[Error: {req_id_action[1]} not found in {patterns.keys()}]"

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

    # endregion

    # region Set values in AiData class from API

    def set_sim_methode(self, name: str) -> None:
        self.__ai_data.set_sim_methode(name)

    def set_sim_threshold(self, threshold: float) -> None:
        self.__ai_data.set_sim_threshold(threshold)

    def set_flag_system(self, flag_system: bool) -> None:
        self.__ai_data.update_progress(AiDataEnum.FLAGS, AiDataEnum.SYSTEM, flag_system)

    def set_flag_ai(self, flag_ai: bool) -> None:
        self.__ai_data.update_progress(AiDataEnum.FLAGS, AiDataEnum.AI, flag_ai)

    def set_ai_methode(self, name: str) -> None:
        self.__ai_data.set_ai_methode(name)

    def set_ai_model(self, name: str) -> None:
        self.__ai_data.set_ai_model(name)

    # endregion

    # region Get data from AiData class for API

    def get_full_info_init_site(self) -> dict:
        return self.__ai_data.get_full_info_init_site()

    def get_matrix(self) -> tuple[list[list[float]], dict] | None:
        return self.__ai_data.get_cluster_matrix()

    def get_log_from_id(self, req_id: str) -> dict:
        return self.__ai_data.requirement_log.get_data_by_req_id(req_id)

    # endregion

    # region Automated Ai formalization thread methods

    def __load_requirements_to_queue(self, rid: str) -> (Queue, frozenset, list[reqtransformer.Requirement]):
        """Loads and queues requirements for AI formalization based on the given ID (with clusters)"""

        req_queue = Queue()
        l_cluster = None
        requirement_with_formalization = []
        for cl in self.__ai_data.get_clusters():
            if rid in cl:
                if cl in self.__locked_cluster:
                    logging.info(f"Cluster {cl} is already locked, stopping the process.")
                    return req_queue, l_cluster, requirement_with_formalization
                self.__locked_cluster.append(cl)
                l_cluster = cl
                for req_id in cl:
                    if req_id in self.__locked_ids:
                        continue
                    requirement = hanfor_flask.current_app.db.get_object(reqtransformer.Requirement, req_id)
                    if check_ai_should_formalized(requirement):
                        self.__locked_ids.append(req_id)
                        req_queue.put(requirement)
                        continue
                    if check_template_for_ai_formalization(requirement):
                        requirement_with_formalization.append(requirement)
                        continue
                break
        return req_queue, l_cluster, requirement_with_formalization

    def __mother_thread_of_ai_formalization(
        self,
        req_queue: Queue,
        requirement_with_formalization: list[reqtransformer.Requirement],
        stop_event_ai: Event,
        l_cluster: frozenset,
    ) -> None:
        """Processes requirements from the queue using AI formalization in parallel threads"""

        threads = []
        while not req_queue.empty():
            if stop_event_ai.is_set():
                break
            requirement_to_formalize = req_queue.get()
            formalize_object = AIFormalization(
                requirement_to_formalize,
                requirement_with_formalization,
                stop_event_ai,
                self.ai_processing_queue,
                self.__ai_data.get_activ_ai_method_object().create_prompt,
                self.__ai_data.get_activ_ai_method_object().parse_ai_response,
                self.__ai_data.get_used_variables(),
                self.__ai_data.get_activ_ai_model(),
                self.__ai_data.get_flags()[AiDataEnum.AI],
                self.__ai_data.requirement_log.add_data,
            )
            self.__ai_data.add_formalization_object(formalize_object)
            logging.debug(requirement_to_formalize.to_dict())
            processing_thread = Thread(target=self.__process_queue_element, args=(formalize_object,), daemon=True)
            processing_thread.start()
            threads.append(processing_thread)
        for thread in threads:
            thread.join()
        if l_cluster:
            for x in l_cluster:
                if x in self.__locked_ids:
                    self.__locked_ids.remove(x)
            if l_cluster in self.__locked_cluster:
                self.__locked_cluster.remove(l_cluster)
        if stop_event_ai.is_set():
            logging.info("Terminated ai formalization")
        else:
            logging.info("Finished processing the queue.")
        logging.debug(self.__locked_ids)

    def __update_used_variables(self) -> None:
        """Return list of used variables from the database with Typ, etc"""
        self.__ai_data.set_used_variables(
            [x.to_dict({}) for x in hanfor_flask.current_app.db.get_objects(reqtransformer.Variable).values()]
        )

    def __process_queue_element(self, formalize_object: AIFormalization) -> None:
        """Processes a single AI formalization task from the queue"""
        formalize_object.run_formalization_process(self.ai_statistic, self.__ai_data.get_activ_ai_method_object().name)
        if self.stop_event_ai.is_set() or formalize_object.status.startswith("terminated"):
            logging.warning(formalize_object.status)
            return
        if formalize_object.status == "complete":
            formalization_integration(formalize_object.formalized_output, formalize_object.requirement_to_formalize)

    # endregion


# region Helper functions for processing requirements


def check_template_for_ai_formalization(req: reqtransformer.Requirement) -> bool:
    """Method which checks if the Requirement can be used as example for Ai formalization."""

    req = req.to_dict(include_used_vars=True)
    return "has_formalization" in req["tags"]


def check_ai_should_formalized(requirement: reqtransformer.Requirement) -> bool:
    """Method which checks if the Requirement can be Ai formalized."""

    return not requirement.to_dict(include_used_vars=True)["formal"]


def formalization_integration(formalization: dict, requirement: reqtransformer.Requirement) -> None:
    """Method which inserts the Ai formalization into the database."""
    # TODO (Waiting for requirement.update_formalization not needing the app (out of context area) meanwhile through API)

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


# endregion
