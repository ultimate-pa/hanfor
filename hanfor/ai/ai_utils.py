from threading import Lock
from time import time
from typing import Optional
import logging
from hanfor.ai import ai_config
from hanfor.ai.interfaces.ai_interface import load_ai_prompt_parse_methods, AIFormalization
from hanfor.ai.interfaces.similarity_interface import load_similarity_methods
from hanfor.ai.ai_enum import AiDataEnum
from hanfor.ai.strategies.ai_prompt_parse_abstract_class import AiPromptParse
from hanfor.ai.strategies.similarity_abstract_class import SimilarityAlgorithm


class AiProcessingQueue:
    """Manages the queue for AI requests, handling both running and waiting requests"""

    max_ai_requests: int = ai_config.MAX_CONCURRENT_AI_REQUESTS

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
                    self.__up_prog()
                return False

    def __up_prog(self):
        self.__update_progress(AiDataEnum.AI, AiDataEnum.QUEUED, len(self.current_waiting))
        self.__update_progress(AiDataEnum.AI, AiDataEnum.RUNNING, len(self.current_ai_request))

    def complete_request(self, req_id):
        self.current_ai_request.remove(req_id)
        self.__up_prog()

    def terminated(self, req_id: str):
        if req_id in self.current_waiting:
            self.current_waiting.remove(req_id)
        if req_id in self.current_ai_request:
            self.current_ai_request.remove(req_id)
        self.__up_prog()


class AiStatistic:
    """Handles statistics related to AI processes, tracking tries and status messages for all model and method combos"""

    def __init__(self):
        self.lock = Lock()
        self.model_method_status_count = {}

    def add_status(self, model: str, methode: str, status: str) -> None:
        with self.lock:
            if model not in self.model_method_status_count:
                self.model_method_status_count[model] = {}

            if methode not in self.model_method_status_count[model]:
                self.model_method_status_count[model][methode] = {}

            if status not in self.model_method_status_count[model][methode]:
                self.model_method_status_count[model][methode][status] = 0

            self.model_method_status_count[model][methode][status] += 1

    def add_try_count(self, model: str, methode: str, count: int) -> None:
        with self.lock:
            if "try_count" not in self.model_method_status_count[model][methode]:
                self.model_method_status_count[model][methode]["try_count"] = []
            self.model_method_status_count[model][methode]["try_count"].append(count)

    def get_status_report(self) -> list[dict[str, str | int | list[dict[str, str | int]]]]:
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

                        status_table.append({"Status": status, "Total": count, "Percentage": round(percentage, 2)})
                report.append(
                    {
                        "Model": model,
                        "Prompt_gen": method,
                        "Avg_try_count": round(avg_try_count, 2),
                        "Status_table": status_table,
                    }
                )
        return report


class AiData:
    """Object containing all data and methods to process those for the AI feature"""

    def __init__(self, ai_statistic: AiStatistic):
        self.__ai_system_data: dict[AiDataEnum, dict[AiDataEnum, bool | int | str]] = {
            AiDataEnum.FLAGS: {
                AiDataEnum.SYSTEM: ai_config.AUTO_UPDATE_ON_REQUIREMENT_CHANGE,
                AiDataEnum.AI: ai_config.ENABLE_API_AI_REQUESTS,
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
        self.__activ_similarity_method: str = ai_config.STANDARD_SIMILARITY_METHOD
        self.__sim_threshold = self.__similarity_methods[self.__activ_similarity_method].standard_threshold

        self.__formalization_objects: list[AIFormalization] = []
        self.__ai_prompt_parse_methods: dict[str, AiPromptParse] = load_ai_prompt_parse_methods()
        self.__activ_ai_prompt_parse_method: str = ai_config.STANDARD_AI_PROMPT_PARSE_METHOD
        self.__used_variables: list[dict] = [{}]
        self.__activ_ai_model: str = ai_config.STANDARD_AI_MODEL
        self.__ai_models: dict[str, str] = ai_config.AI_MODEL_NAMES

        self.__ai_statistic = ai_statistic

    def get_full_info(self) -> dict:
        ret = {
            "cluster_status": self.__get_info_cluster_status(),
            "clusters": self.__get_clusters(),
            "ai_status": self.__get_info_ai_status(),
            "ai_formalization": self.__get_ai_formalization_progress(),
            "flags": self.__get_info_flags(),
            "sim_methods": self.__get_info_sim_methods(),
            "ai_methods": self.__get_info_ai_methods(),
            "ai_models": self.__get_info_ai_models(),
            "ai_statistic": self.__ai_statistic.get_status_report(),
        }
        return ret

    def update_progress(
        self, progress_outer: AiDataEnum, progress_inner: Optional[AiDataEnum], update: any, increment: bool = False
    ):
        if increment and type(update) is int:
            update = self.__ai_system_data[progress_outer][progress_inner] + update
        if progress_inner:
            self.__ai_system_data[progress_outer][progress_inner] = update
        else:
            self.__ai_system_data[progress_outer] = update

    def get_sim_function(self) -> callable:
        return self.__similarity_methods[self.__activ_similarity_method].compare

    def get_sim_threshold(self) -> float:
        return self.__sim_threshold

    def get_flags(self) -> dict[AiDataEnum, bool]:
        return self.__ai_system_data[AiDataEnum.FLAGS]

    def get_clusters(self) -> set[frozenset[str]]:
        return self.__clusters or set()

    def get_cluster_matrix(self) -> tuple[list[list[float]], dict]:
        return self.__cluster_matrix

    def get_activ_ai_model(self) -> str:
        return self.__activ_ai_model

    def get_activ_ai_method_object(self) -> AiPromptParse:
        return self.__ai_prompt_parse_methods[self.__activ_ai_prompt_parse_method]

    def get_used_variables(self) -> list[dict]:
        return self.__used_variables

    def set_used_variables(self, used_variables: list[dict]):
        self.__used_variables = used_variables

    def set_sim_methode(self, name: str) -> None:
        if name in self.__similarity_methods.keys():
            logging.debug(f"Setting similarity method: {name}")
            self.__activ_similarity_method = name
            self.__sim_threshold = self.__similarity_methods[name].standard_threshold

    def set_sim_threshold(self, threshold: float) -> None:
        logging.debug(f"Setting similarity threshold: {threshold}")
        self.__sim_threshold = threshold

    def set_ai_methode(self, name: str) -> None:
        if name in self.__ai_prompt_parse_methods.keys():
            logging.debug(f"Setting ai method: {name}")
            self.__activ_ai_prompt_parse_method = name

    def set_ai_model(self, name: str) -> None:
        if name in self.__ai_models.keys():
            logging.debug(f"Setting ai model: {name}")
            self.__activ_ai_model = name

    def set_clusters(self, clusters: set[frozenset[str]]) -> None:
        self.__clusters = clusters

    def set_cluster_matrix(self, cluster_matrix: tuple[list[list[float]], dict]) -> None:
        self.__cluster_matrix = cluster_matrix

    def add_formalization_object(self, formalization_object: AIFormalization) -> None:
        self.__formalization_objects.append(formalization_object)

    def __get_info_cluster_status(self) -> dict:
        return {
            "status": self.__ai_system_data[AiDataEnum.CLUSTER][AiDataEnum.STATUS].value,
            "processed": self.__ai_system_data[AiDataEnum.CLUSTER][AiDataEnum.PROCESSED],
            "total": self.__ai_system_data[AiDataEnum.CLUSTER][AiDataEnum.TOTAL],
        }

    def __get_clusters(self):
        if self.__clusters:
            return [list(cluster) for cluster in self.__clusters]
        return []

    def __get_info_ai_status(self) -> dict:
        return {
            "running": self.__ai_system_data[AiDataEnum.AI][AiDataEnum.RUNNING],
            "queued": self.__ai_system_data[AiDataEnum.AI][AiDataEnum.QUEUED],
            "response": self.__ai_system_data[AiDataEnum.AI][AiDataEnum.RESPONSE],
            "query": self.__ai_system_data[AiDataEnum.AI][AiDataEnum.QUERY],
        }

    def __get_ai_formalization_progress(self) -> list[dict[str, any]]:
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
            for f_obj in self.__formalization_objects
        ]

    def __get_info_flags(self) -> dict:
        return {
            "system": self.__ai_system_data[AiDataEnum.FLAGS][AiDataEnum.SYSTEM],
            "ai": self.__ai_system_data[AiDataEnum.FLAGS][AiDataEnum.AI],
        }

    def __get_info_sim_methods(self) -> (float, list):
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
        methods_info = []
        if self.__ai_prompt_parse_methods:
            for name, method in self.__ai_prompt_parse_methods.items():
                method_info = {
                    "name": name,
                    "description": method.description,
                    "selected": name == self.__activ_ai_prompt_parse_method,
                }
                methods_info.append(method_info)
        return methods_info

    def __get_info_ai_models(self) -> list:
        methods_info = []
        if self.__ai_prompt_parse_methods:
            for name, desc in self.__ai_models.items():
                method_info = {
                    "name": name,
                    "description": desc,
                    "selected": name == self.__activ_ai_model,
                }
                methods_info.append(method_info)
        return methods_info

    def __cleanup_old_formalizations(self):
        current_time = time()
        self.__formalization_objects = [
            f_obj
            for f_obj in self.__formalization_objects
            if f_obj.del_time is None or (current_time - f_obj.del_time < 10)
        ]
