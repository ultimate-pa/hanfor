from dataclasses import dataclass, field, asdict
import json
from datetime import datetime
from os import path
from flask import current_app
from utils import get_requirements
from pydantic import parse_obj_as

from defaults import Color
from configuration.ultimate_config import AUTOMATED_TAGS
from tags.tags import TagsApi
from reqtransformer import Requirement

from json_db_connector.json_db import DatabaseTable, TableType, DatabaseID, DatabaseField

FILE_VERSION = 0


@DatabaseTable(TableType.Folder)
@DatabaseID("job_id", str)
@DatabaseField("requirement_file", str)
@DatabaseField("toolchain_id", str)
@DatabaseField("toolchain_xml", str)
@DatabaseField("usersettings_name", str)
@DatabaseField("usersettings_json", str)
@DatabaseField("selected_requirements", list[tuple[str, int]], [])
@DatabaseField("results", list[dict], [])
@DatabaseField("result_requirements", list[tuple[str, int]], [])
@DatabaseField("api_url", str)
@DatabaseField("job_status", str)
@DatabaseField("request_time", datetime)
@DatabaseField("last_update", datetime)
@dataclass(kw_only=True)
class UltimateJob:
    job_id: str
    requirement_file: str
    toolchain_id: str
    toolchain_xml: str
    usersettings_name: str
    usersettings_json: str
    selected_requirements: list[tuple[str, int]] = field(default_factory=list)  # (requirement_id, # of formalisations)
    results: list[dict] = field(default_factory=list)
    result_requirements: list[tuple[str, int]] = field(default_factory=list)  # (requirement_id, # of formalisations)
    api_url: str = ""
    job_status: str = "scheduled"
    request_time: str = datetime.now()
    last_update: str = datetime.now()

    @classmethod
    def make(
        cls,
        job_id: str,
        requirement_file: str,
        toolchain_id: str,
        toolchain_xml: str,
        usersettings_name: str,
        usersettings_json: str,
        api_url: str,
        selected_requirements: list[str],
    ):
        if selected_requirements == "all":
            selected_requirements = get_all_requirement_ids()
        requirements = calculate_req_id_occurrence(requirement_file, selected_requirements)
        return cls(
            job_id=job_id,
            requirement_file=requirement_file,
            toolchain_id=toolchain_id,
            toolchain_xml=toolchain_xml,
            usersettings_name=usersettings_name,
            usersettings_json=usersettings_json,
            api_url=api_url,
            selected_requirements=requirements,
        )

    def save_to_file(self, *, save_dir: str = None, file_name: str = None) -> None:
        if save_dir is not None:
            with open(path.join(save_dir, f"{self.job_id}.json"), "w") as save_file:
                save_file.write(json.dumps(asdict(self), indent=4))
        elif file_name is not None:
            with open(file_name, "w") as save_file:
                save_file.write(json.dumps(asdict(self), indent=4))
        else:
            raise Exception("Job can not be saved without a file_name or the save_dir")

    def update(self, data: dict) -> None:
        if not data["requestId"] == self.job_id:
            raise Exception("Missmatch of requestID")
        last_status = self.job_status
        object.__setattr__(self, "last_update", datetime.now().strftime("%Y.%m.%d, %H:%M:%S.%f"))
        object.__setattr__(self, "job_status", data["status"])
        if not data["result"] == "":
            object.__setattr__(self, "results", data["result"])
        if last_status == "scheduled" and self.job_status == "done":
            process_result(self)

    def get(self) -> dict:
        return {
            "status": self.job_status,
            "requestId": self.job_id,
            "result": self.results,
            "request_time": self.request_time,
            "last_update": self.last_update,
            "selected_requirements": self.selected_requirements,
            "result_requirements": self.result_requirements,
        }

    def get_download(self) -> dict:
        return asdict(self)


def calculate_req_id_occurrence(requirement_file: str, selected_requirements: list[str]) -> list[tuple[str, int]]:
    req: dict[str, tuple[str, int]] = {}
    for req_id in selected_requirements:
        req[req_id.replace("-", "_") + "_"] = (req_id, 0)
    for line in requirement_file.split("\n"):
        if line.startswith("INPUT") or line.startswith("CONST") or line == "":
            continue
        for req_id_formatted in req:
            if line.startswith(req_id_formatted):
                req[req_id_formatted] = (req[req_id_formatted][0], req[req_id_formatted][1] + 1)
                continue

    requirements: list[(str, int)] = []
    for req_id_formatted in req:
        requirements.append(req[req_id_formatted])
    return requirements


def check_ultimate_tag_is_available() -> None:
    tags_api = TagsApi()
    try:
        _ = tags_api.get("Ultimate_raw_data")
    except ValueError:
        # ultimate_raw_data tag is not available
        tags_api.add("Ultimate_raw_data", Color.BS_GRAY.value, False, "")
        pass


def get_all_requirement_ids() -> list[str]:
    """ "
    returns a list of (requirementID, requirementID without -)
    """
    requirements = get_requirements(current_app)
    return [requirement.rid for requirement in requirements]


def add_ultimate_result_to_requirement(
    requirement_id: str, ultimate_results: list[dict], ultimate_job: UltimateJob
) -> None:
    requirement = current_app.db.get_object(Requirement, requirement_id)
    if not requirement:
        return
    tmp = f"# {ultimate_job.job_id} ({ultimate_job.last_update})\n"
    for result in ultimate_results:
        result_text = result["longDesc"].replace("\n ", "\n\t")
        tmp += f"\n{result['type']}: {result_text}"
    if "Ultimate_raw_data" in requirement.tags:
        requirement.tags["Ultimate_raw_data"] = f"{tmp}\n\n---\n\n{requirement.tags['Ultimate_raw_data']}"
    else:
        requirement.tags["Ultimate_raw_data"] = f"{tmp}"

    requirement.store()


def process_result(ultimate_job: UltimateJob) -> None:
    check_ultimate_tag_is_available()
    requirements = []
    for req, count in ultimate_job.selected_requirements:
        if count == 0:
            continue
        requirements.append((req, req.replace("-", "_") + "_"))
    tags: dict[str, list[dict]] = {}
    req_results: dict[str, int] = {}
    for result in ultimate_job.results:
        for requirement in requirements:
            if requirement[1] in result["longDesc"]:
                if requirement[0] in tags:
                    tags[requirement[0]].append(result)
                    req_results[requirement[0]] += 1
                else:
                    tags[requirement[0]] = [result]
                    req_results[requirement[0]] = 1
    req_results_list = [(req_id, val) for req_id, val in req_results.items()]
    object.__setattr__(ultimate_job, "result_requirements", req_results_list)
    if AUTOMATED_TAGS:
        for requirement, results in tags.items():
            add_ultimate_result_to_requirement(requirement, results, ultimate_job)
