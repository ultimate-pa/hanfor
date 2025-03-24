import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from hanfor_flask import current_app

from configuration.ultimate_config import AUTOMATED_TAGS
from lib_core.data import Requirement, SessionValue
from lib_core.utils import get_requirements

from json_db_connector.json_db import DatabaseTable, TableType, DatabaseID, DatabaseField

FILE_VERSION = 0
DATETIME_STR_FORMAT = "%Y.%m.%d, %H:%M:%S.%f"


@DatabaseTable(TableType.Folder)
@DatabaseID("job_id", str)
@DatabaseField("requirement_file", str)
@DatabaseField("toolchain_id", str)
@DatabaseField("toolchain_xml", str)
@DatabaseField("usersettings_name", str)
@DatabaseField("usersettings_json", str)
@DatabaseField("selected_requirements", dict, {})
@DatabaseField("results", list[dict], [])
@DatabaseField("result_requirements", dict, {})
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
    selected_requirements: dict[str, int] = field(default_factory=dict)  # (requirement_id, # of formalisations)
    results: list[dict] = field(default_factory=list)
    result_requirements: dict[str, int] = field(default_factory=dict)  # (requirement_id, # of formalisations)
    api_url: str = ""
    job_status: str = "scheduled"
    request_time: datetime = datetime.now()
    last_update: datetime = datetime.now()

    def update(self, data: dict) -> None:
        if not data["requestId"] == self.job_id:
            raise Exception("Missmatch of requestID")
        last_status = self.job_status
        object.__setattr__(self, "last_update", datetime.now())
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
            "request_time": self.request_time.strftime(DATETIME_STR_FORMAT),
            "last_update": self.last_update.strftime(DATETIME_STR_FORMAT),
            "selected_requirements": self.selected_requirements,
            "result_requirements": self.result_requirements,
        }

    def get_download(self) -> dict:
        tmp = asdict(self)
        tmp["request_time"] = self.request_time.strftime(DATETIME_STR_FORMAT)
        tmp["last_update"] = self.last_update.strftime(DATETIME_STR_FORMAT)
        return tmp


def calculate_req_id_occurrence(requirement_file: str, selected_requirements: list[str]) -> dict[str, int]:
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

    requirements: dict[str, int] = {}
    for req_id_formatted in req:
        requirements[req[req_id_formatted][0]] = req[req_id_formatted][1]
    return requirements


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
    tmp = f"# {ultimate_job.job_id} ({ultimate_job.last_update.strftime(DATETIME_STR_FORMAT)})\n"
    for result in ultimate_results:
        result_text = result["longDesc"].replace("\n ", "\n\t")
        tmp += f"\n{result['type']}: {result_text}"
    ultimate_raw_data_tag = current_app.db.get_object(SessionValue, "TAG_Ultimate_raw_data").value
    if ultimate_raw_data_tag in requirement.tags:
        requirement.tags[ultimate_raw_data_tag] = f"{tmp}\n\n---\n\n{requirement.tags[ultimate_raw_data_tag]}"
    else:
        requirement.tags[ultimate_raw_data_tag] = f"{tmp}"

    current_app.db.update()


def process_result(ultimate_job: UltimateJob) -> None:
    requirements = []
    for req, count in ultimate_job.selected_requirements.items():
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
    object.__setattr__(ultimate_job, "result_requirements", req_results)
    if AUTOMATED_TAGS:
        for requirement, results in tags.items():
            add_ultimate_result_to_requirement(requirement, results, ultimate_job)
