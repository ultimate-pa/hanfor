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

FILE_VERSION = 0


@dataclass(frozen=True, kw_only=True)
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
    request_time: str = datetime.now().strftime("%Y.%m.%d, %H:%M:%S.%f")
    last_update: str = datetime.now().strftime("%Y.%m.%d, %H:%M:%S.%f")

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

    @classmethod
    def from_file(cls, *, save_dir: str = None, job_id: str = None, file_name: str = None):
        # generate file_name from save_dir and job_id
        if file_name is None:
            if save_dir is None:
                raise Exception("save_dir is not defined!")
            if job_id is None:
                raise Exception("job_id is not defined!")
            file_name = path.join(save_dir, f"{job_id}.json")

        # check if file exist
        if not path.isfile(file_name):
            raise Exception(f"{file_name} can not be found!")

        # read file
        with open(file_name, "r") as save_file:
            data = json.load(save_file)
        job = parse_obj_as(cls, data)
        # check for old file version
        # add all requirements
        if not job.selected_requirements:
            all_req_ids = get_all_requirement_ids()
            selected_requirements = calculate_req_id_occurrence(job.requirement_file, all_req_ids)
            object.__setattr__(job, "selected_requirements", selected_requirements)
            job.save_to_file(file_name=file_name)
        # add all requirements with results
        if not job.result_requirements and job.job_status == "done":
            requirements = []
            for req, count in job.selected_requirements:
                if count == 0:
                    continue
                requirements.append((req, req.replace("-", "_") + "_"))
            req_results: dict[str, int] = {}
            for result in job.results:
                for requirement in requirements:
                    if requirement[1] in result["longDesc"]:
                        if requirement[0] in req_results:
                            req_results[requirement[0]] += 1
                        else:
                            req_results[requirement[0]] = 1
            req_results_list = [(req_id, val) for req_id, val in req_results.items()]
            object.__setattr__(job, "result_requirements", req_results_list)
            job.save_to_file(file_name=file_name)
        return job

    def save_to_file(self, *, save_dir: str = None, file_name: str = None) -> None:
        if save_dir is not None:
            with open(path.join(save_dir, f"{self.job_id}.json"), "w") as save_file:
                save_file.write(json.dumps(asdict(self), indent=4))
        elif file_name is not None:
            with open(file_name, "w") as save_file:
                save_file.write(json.dumps(asdict(self), indent=4))
        else:
            raise Exception("Job can not be saved without a file_name or the save_dir")

    def update(self, data: dict, save_dir: str) -> None:
        if not data["requestId"] == self.job_id:
            raise Exception("Missmatch of requestID")
        last_status = self.job_status
        object.__setattr__(self, "last_update", datetime.now().strftime("%Y.%m.%d, %H:%M:%S.%f"))
        object.__setattr__(self, "job_status", data["status"])
        if not data["result"] == "":
            object.__setattr__(self, "results", data["result"])
        self.save_to_file(save_dir=save_dir)
        if last_status == "scheduled" and self.job_status == "done":
            process_result(self, save_dir)

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
    if tags_api.get("Ultimate_raw_data") == {}:
        # ultimate_raw_data tag is not available
        tags_api.add("Ultimate_raw_data", Color.BS_GRAY.value, False, "")


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


def process_result(ultimate_job: UltimateJob, save_dir: str) -> None:
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
    ultimate_job.save_to_file(save_dir=save_dir)
    if AUTOMATED_TAGS:
        for requirement, results in tags.items():
            add_ultimate_result_to_requirement(requirement, results, ultimate_job)
