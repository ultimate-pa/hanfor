import importlib
import os
from threading import Lock
from time import time
from typing import Optional
import logging
from ai.interfaces.ai_interface import load_ai_prompt_parse_methods, AIFormalization
from ai.ai_enum import AiDataEnum
from ai.strategies.ai_prompt_parse_abstract_class import AiPromptParse
from ai.strategies.similarity_abstract_class import SimilarityAlgorithm
from tinyflux import TinyFlux, Point, TagQuery
from datetime import datetime
from ai.ai_socket import send_ai_update
from configuration import ai_formalization_config


class RequirementLog:
    """Handles logging and retrieval of AI requirement data using TinyFlux"""

    def __init__(self, data_folder: str):
        self.db = TinyFlux(os.path.join(data_folder, "ai_requirement_log.csv"))
        self.entry_counters: dict[str, int] = {}
        self.req_ids: list[str] = []
        self.lock = Lock()

    def set_ids(self, id_list: list[str]) -> None:
        """Sets requirement IDs and loads corresponding log data from the database"""

        with self.lock:
            self.req_ids = id_list
            if self.db is None:
                raise ValueError("TinyFlux database is not initialized.")
            tags = TagQuery()
            for req_id in id_list:
                self.entry_counters[req_id] = len(self.db.search(tags.req_id == req_id))
            logging.info(f"loaded ai_requirement_log.csv")

    def add_data(self, req_id: str, data: dict[str, any]) -> None:
        """Adds a new data entry for a given requirement ID"""

        with self.lock:
            if self.db is None:
                raise ValueError("TinyFlux database is not initialized.")

            timestamp = datetime.now()
            formatted_time = timestamp.strftime("%Y-%m-%d/%H:%M:%S.%f")
            self.entry_counters[req_id] += 1
            unique_timestamp = f"{formatted_time}_{self.entry_counters[req_id]}"
            data["unique_timestamp"] = unique_timestamp
            data["req_id"] = req_id

            point = Point(time=timestamp, tags=data)
            self.db.insert(point)

    def get_data_by_req_id(self, req_id: str) -> dict:
        """Retrieves all data entries for a specific requirement ID"""

        tags = TagQuery()
        points = self.db.search(tags.req_id == req_id)

        result = {}
        for point in points:
            unique_timestamp = point.tags.get("unique_timestamp")
            filtered_tags = {k: v for k, v in point.tags.items() if k not in ["unique_timestamp", "req_id"]}
            result[unique_timestamp] = filtered_tags

        return result

    def get_ids(self) -> list:
        """Returns the list of all requirement IDs"""

        return self.req_ids


class AiProcessingQueue:
    """Manages the queue for AI requests, handling both running and waiting requests"""

    def __init__(self, update_progress_function) -> None:
        self.current_ai_request = []
        self.current_waiting = []
        self.lock = Lock()
        self.__update_progress_extern_function = update_progress_function

    def add_request(self, req_id: str) -> bool:
        """Adds a new request to the queue. Returns True if the requester can run, False if put in queued."""

        with self.lock:
            if len(self.current_ai_request) < self.max_ai_requests:
                if req_id in self.current_waiting:
                    self.current_waiting.remove(req_id)
                self.current_ai_request.append(req_id)
                self.__update_progress_intern()
                return True
            else:
                if req_id not in self.current_waiting:
                    self.current_waiting.append(req_id)
                    self.__update_progress_intern()
                return False

    def __update_progress_intern(self) -> None:
        """Updates the progress of running and queued AI requests"""

        self.__update_progress_extern_function(AiDataEnum.AI, AiDataEnum.QUEUED, len(self.current_waiting))
        self.__update_progress_extern_function(AiDataEnum.AI, AiDataEnum.RUNNING, len(self.current_ai_request))

    def complete_request(self, req_id: str) -> None:
        """Marks a request as completed and updates the progress"""

        self.current_ai_request.remove(req_id)
        self.__update_progress_intern()

    def terminated(self, req_id: str) -> None:
        """Removes a request from both running and waiting queues when terminated"""

        if req_id in self.current_waiting:
            self.current_waiting.remove(req_id)
        if req_id in self.current_ai_request:
            self.current_ai_request.remove(req_id)
        self.__update_progress_intern()


class AiStatistic:
    """Handles statistics related to AI processes, tracking tries and status messages for all model and method combos"""

    def __init__(self):
        self.__send_updated_data = None
        self.lock = Lock()
        self.model_method_status_count = {}

    def add_status(self, model: str, methode: str, status: str) -> None:
        """Adds a status entry for a given model and method."""

        with self.lock:
            if model not in self.model_method_status_count:
                self.model_method_status_count[model] = {}

            if methode not in self.model_method_status_count[model]:
                self.model_method_status_count[model][methode] = {}

            if status not in self.model_method_status_count[model][methode]:
                self.model_method_status_count[model][methode][status] = 0

            self.model_method_status_count[model][methode][status] += 1
        self.__send_updated_data(AiDataEnum.AI, AiDataEnum.STATISTICS)

    def add_try_count(self, model: str, methode: str, count: int) -> None:
        """Adds the number of tries for a given model and method."""

        with self.lock:
            if "try_count" not in self.model_method_status_count[model][methode]:
                self.model_method_status_count[model][methode]["try_count"] = []
            self.model_method_status_count[model][methode]["try_count"].append(count)

    def get_status_report(self) -> list[dict[str, str | int | list[dict[str, str | int]]]]:
        """Generates a report summarizing status counts and average tries for each model-method"""

        report = []
        for model, methods in self.model_method_status_count.items():
            for method, status_data in methods.items():
                try_count = status_data.get("try_count", [])
                total_tries = sum(try_count) if try_count else 0
                avg_try_count = total_tries / len(try_count) if try_count else 0

                status_table = []
                total_statuses = sum(count for key, count in status_data.items() if key != "try_count")
                for status, count in status_data.items():
                    if status != "try_count":
                        percentage = (count / total_statuses) * 100

                        status_table.append({"status": status, "total": count, "percentage": round(percentage, 2)})
                report.append(
                    {
                        "model": model,
                        "prompt_gen": method,
                        "avg_try_count": round(avg_try_count, 2),
                        "status_table": status_table,
                    }
                )
        return report

    def set_send_update_method(self, send_updated_data: callable) -> None:
        """Sets the method for sending updates (via socket)"""

        self.__send_updated_data = send_updated_data


class AiData:
    """Object containing all data and methods to process those for the AI feature"""

    def __init__(self, ai_statistic: AiStatistic) -> None:
        self.socketio = None
        self.__ai_system_data: dict[AiDataEnum, dict[AiDataEnum, bool | int | str | AiDataEnum]] = {
            AiDataEnum.FLAGS: {
                AiDataEnum.SYSTEM: ai_formalization_config.AUTO_UPDATE_ON_REQUIREMENT_CHANGE,
                AiDataEnum.AI: ai_formalization_config.ENABLE_API_AI_REQUESTS,
            },
            AiDataEnum.CLUSTER: {
                AiDataEnum.STATUS: AiDataEnum.NOT_STARTED,
                AiDataEnum.PROCESSED: 0,
                AiDataEnum.TOTAL: 0,
            },
            AiDataEnum.AI: {AiDataEnum.RUNNING: 0, AiDataEnum.QUEUED: 0, AiDataEnum.RESPONSE: "", AiDataEnum.QUERY: ""},
        }

        self.__clusters: Optional[set[frozenset[str]]] = None
        self.__cluster_matrix: Optional[tuple[list[list[float]], dict]] = None
        self.__similarity_methods: dict[str, SimilarityAlgorithm] = load_similarity_methods()
        self.__activ_similarity_method: str = ai_formalization_config.STANDARD_SIMILARITY_METHOD
        self.__sim_threshold = self.__similarity_methods[self.__activ_similarity_method].standard_threshold

        self.__formalization_objects: list[AIFormalization] = []
        self.__ai_prompt_parse_methods: dict[str, AiPromptParse] = load_ai_prompt_parse_methods()
        self.__activ_ai_prompt_parse_method: str = ai_formalization_config.STANDARD_AI_PROMPT_PARSE_METHOD
        self.__used_variables: list[dict] = [{}]

        self.__ai_statistic = ai_statistic
        self.__ai_statistic.set_send_update_method(self.__send_updated_data)
        self.requirement_log: Optional[RequirementLog] = None

    def set_data_folder(self, data_folder: str, socketio) -> None:
        """Setting the data folder for the location of the log file."""
        self.socketio = socketio
        self.requirement_log = RequirementLog(data_folder)

    def get_full_info_init_site(self) -> dict:
        """Returns all data needed by the API to load the site"""

        ret = {
            "cluster_status": self.__get_info_cluster_status(),
            "clusters": self.__get_clusters(),
            "ai_status": self.__get_info_ai_status(),
            "ai_formalization": self.__get_ai_formalization_progress(),
            "flags": self.__get_info_flags(),
            "sim_methods": self.__get_info_sim_methods(),
            "threshold": self.__sim_threshold,
            "ai_methods": self.__get_info_ai_methods(),
            # "ai_models": self.__get_info_ai_models(),
            "ai_statistic": self.__ai_statistic.get_status_report(),
            "req_ids": self.requirement_log.get_ids(),
            "ai_formalization_deletion_time": ai_formalization_config.DELETION_TIME_AFTER_COMPLETION_FORMALIZATION,
        }
        return ret

    def __send_updated_data(self, updated_data: AiDataEnum, specified_data: Optional[AiDataEnum]) -> None:
        """Prepares and sends updated data based on the provided enums with socket"""

        send_dict = {}
        match updated_data:
            case AiDataEnum.FLAGS:
                send_dict = {"flags": self.__get_info_flags()}
            case AiDataEnum.CLUSTER:
                match specified_data:
                    case AiDataEnum.STATUS:
                        send_dict = {"cluster_status": self.__get_info_cluster_status()}
                    case AiDataEnum.METHOD:
                        send_dict = {"sim_methods": self.__get_info_sim_methods()}
                    case AiDataEnum.CLUSTER:
                        send_dict = {"clusters": self.__get_clusters()}
            case AiDataEnum.AI:
                match specified_data:
                    case AiDataEnum.MODEL:
                        send_dict = {"activ_ai_model": self.get_activ_ai_model_object()[0]}
                    case AiDataEnum.METHOD:
                        send_dict = {"activ_ai_method": self.__activ_ai_prompt_parse_method}
                    case AiDataEnum.STATISTICS:
                        send_dict = {"ai_statistic": self.__ai_statistic.get_status_report()}
                    case AiDataEnum.STATUS:
                        send_dict = {"ai_status": self.__get_info_ai_status()}
                    case AiDataEnum.FORMALIZATION:
                        send_dict = {"ai_formalization": self.__get_ai_formalization_progress()}
        if send_dict:
            send_ai_update(send_dict, self.socketio)

    def update_progress(self, progress_outer: AiDataEnum, progress_inner: Optional[AiDataEnum], update: any):
        """Centralized method to update progress data (flags, Ai and cluster progress info)"""

        match progress_outer:
            case AiDataEnum.FORMALIZATION:
                self.__send_updated_data(AiDataEnum.AI, AiDataEnum.FORMALIZATION)
                return

        if progress_inner:
            self.__ai_system_data[progress_outer][progress_inner] = update
        else:
            self.__ai_system_data[progress_outer] = update

        specified_data = AiDataEnum.STATUS if progress_outer in {AiDataEnum.AI, AiDataEnum.CLUSTER} else None
        self.__send_updated_data(progress_outer, specified_data)

    # region Data retrieval methods (primarily internal use)

    def get_sim_class(self) -> SimilarityAlgorithm:
        return self.__similarity_methods[self.__activ_similarity_method]

    def get_sim_threshold(self) -> float:
        return self.__sim_threshold

    def get_flags(self) -> dict[AiDataEnum, bool]:
        return self.__ai_system_data[AiDataEnum.FLAGS]

    def get_clusters(self) -> set[frozenset[str]]:
        return self.__clusters or set()

    def get_cluster_matrix(self) -> tuple[list[list[float]], dict]:
        return self.__cluster_matrix

    def get_activ_ai_model_object(self) -> tuple[str, dict] | None:
        for name, value in self.__ai_models.items():
            if value["selected"]:
                return name, value
        return None

    def get_activ_ai_method_object(self) -> AiPromptParse:
        return self.__ai_prompt_parse_methods[self.__activ_ai_prompt_parse_method]

    def get_used_variables(self) -> list[dict]:
        return self.__used_variables

    # endregion

    # region API-triggered data updates (external input)

    def set_sim_methode(self, name: str) -> None:
        if name in self.__similarity_methods.keys():
            logging.debug(f"Setting similarity method: {name}")
            self.__activ_similarity_method = name
            self.__sim_threshold = self.__similarity_methods[name].standard_threshold
            self.__send_updated_data(AiDataEnum.CLUSTER, AiDataEnum.METHOD)

    def set_sim_threshold(self, threshold: float) -> None:
        logging.debug(f"Setting similarity threshold: {threshold}")
        self.__sim_threshold = threshold
        self.__send_updated_data(AiDataEnum.CLUSTER, AiDataEnum.METHOD)

    def set_ai_methode(self, name: str) -> None:
        if name in self.__ai_prompt_parse_methods.keys():
            logging.debug(f"Setting ai method: {name}")
            self.__activ_ai_prompt_parse_method = name
            self.__send_updated_data(AiDataEnum.AI, AiDataEnum.METHOD)

    def set_ai_model(self, name: str) -> None:
        if name in self.__ai_models.keys():
            logging.debug(f"Setting ai model: {name}")
            for old_model, value in self.__ai_models.items():
                if value["selected"]:
                    self.__ai_models[old_model]["selected"] = False
            self.__ai_models[name]["selected"] = True
            self.__send_updated_data(AiDataEnum.AI, AiDataEnum.MODEL)

    # endregion

    # region Server-side data updates (internal use only)

    def set_used_variables(self, used_variables: list[dict]) -> None:
        self.__used_variables = used_variables

    def set_clusters(self, clusters: Optional[set[frozenset[str]]]) -> None:
        self.__clusters = clusters
        self.__send_updated_data(AiDataEnum.CLUSTER, AiDataEnum.CLUSTER)

    def set_cluster_matrix(self, cluster_matrix: Optional[tuple[list[list[float]], dict]]) -> None:
        self.__cluster_matrix = cluster_matrix

    def add_formalization_object(self, formalization_object: AIFormalization) -> None:
        self.__formalization_objects.append(formalization_object)

    # endregion

    # region Helper methods for processing information for the API

    def __get_info_cluster_status(self) -> dict:
        """Returns the current status of the clustering process, including status, processed count, and total items"""

        cluster_data = self.__ai_system_data[AiDataEnum.CLUSTER]
        return {
            "status": cluster_data[AiDataEnum.STATUS].value,
            "processed": cluster_data[AiDataEnum.PROCESSED],
            "total": cluster_data[AiDataEnum.TOTAL],
        }

    def __get_clusters(self) -> list:
        """Returns the current clusters as a list of lists. If no clusters exist, returns an empty list"""

        return [list(cluster) for cluster in self.__clusters] if self.__clusters else []

    def __get_info_ai_status(self) -> dict:
        """Returns the current AI system status, including running state, queue, response, and query"""

        ai_status = self.__ai_system_data[AiDataEnum.AI]
        return {
            "running": ai_status[AiDataEnum.RUNNING],
            "queued": ai_status[AiDataEnum.QUEUED],
            "response": ai_status[AiDataEnum.RESPONSE],
            "query": ai_status[AiDataEnum.QUERY],
        }

    def __get_ai_formalization_progress(self) -> list[dict[str, any]]:
        """Returns the progress of AI formalizations with relevant details for each requirement"""

        self.__cleanup_old_formalizations()

        return [
            {
                "id": f_obj.requirement_to_formalize.to_dict().get("id"),
                "status": f_obj.status,
                "prompt": f_obj.prompt,
                "ai_response": f_obj.ai_response,
                "formalized_output": f_obj.formalized_output,
                "try_count": f_obj.try_count,
                "time": f_obj.del_time,
            }
            for f_obj in self.__formalization_objects
        ]

    def __get_info_flags(self) -> dict:
        """Returns the current system and AI flag"""

        flags = self.__ai_system_data[AiDataEnum.FLAGS]
        return {
            "system": flags[AiDataEnum.SYSTEM],
            "ai": flags[AiDataEnum.AI],
        }

    def __get_info_sim_methods(self) -> (float, list):
        """Returns the current similarity threshold and a list of available similarity methods"""

        methods_info = []
        if self.__similarity_methods:
            for name, method in self.__similarity_methods.items():
                method_info = {
                    "name": name,
                    "description": method.description,
                    "interval": method.threshold_interval,
                    "default": method.standard_threshold,
                    "selected": name == self.__activ_similarity_method,
                }
                methods_info.append(method_info)
        return self.__sim_threshold, methods_info

    def __get_info_ai_methods(self) -> list:
        """Returns a list of available AI methods with their name, description, and selection status."""

        return (
            [
                {
                    "name": name,
                    "description": method.description,
                    "selected": name == self.__activ_ai_prompt_parse_method,
                }
                for name, method in self.__ai_prompt_parse_methods.items()
            ]
            if self.__ai_prompt_parse_methods
            else []
        )

    def __get_info_ai_models(self) -> list:
        """Returns a list of AI models with their name, description, and selection status."""
        return (
            [
                {"name": name, "description": value["description"], "selected": value["selected"]}
                for name, value in self.__ai_models.items()
            ]
            if self.__ai_models
            else []
        )

    def __cleanup_old_formalizations(self) -> None:
        """Deletes all formalization objects that have existed longer than a certain time after completion."""
        current_time = time()
        self.__formalization_objects = [
            f_obj
            for f_obj in self.__formalization_objects
            if f_obj.del_time is None
            or (current_time - f_obj.del_time < ai_formalization_config.DELETION_TIME_AFTER_COMPLETION_FORMALIZATION)
        ]

    # endregion


def load_similarity_methods() -> dict[str, SimilarityAlgorithm]:
    """Dynamically loads all similarity algorithms from the specified directory."""

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategies/similarity_methods/")
    methods = {}
    base_package = "ai.strategies.similarity_methods"

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            # Import Modul
            module_name = filename[:-3]
            module_path = f"{base_package}.{module_name}"

            try:
                module = importlib.import_module(module_path)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, SimilarityAlgorithm)
                        and attr is not SimilarityAlgorithm
                    ):
                        try:
                            instance = attr()
                            methods[instance.name] = instance
                        except TypeError as e:
                            logging.warning(f"Class {attr_name} in module {module_path} could not be instantiated: {e}")
            except ModuleNotFoundError as e:
                logging.error(f"Error loading module {module_path}: {e}")
    return methods
