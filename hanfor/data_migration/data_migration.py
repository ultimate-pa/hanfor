import argparse
import logging
import re
from datetime import datetime
from os import path, sep, mkdir, listdir
from shutil import move

from configuration.defaults import Color
from data_migration.my_unpickler import (
    pickle_load_from_dump,
    OldRequirement,
    OldVariableCollection,
    OldUltimateJob,
    OldFormalization,
    OldScopedPattern,
    OldScope,
    OldPattern,
    OldExpression,
)
from json_db_connector.json_db import JsonDatabase, DatabaseKeyError
from lib_core.data import (
    Requirement,
    Formalization,
    Expression,
    ScopedPattern,
    Pattern,
    Variable,
    RequirementEditHistory,
    SessionValue,
    Tag,
)
from lib_core.scopes import Scope
from lib_core.startup import add_custom_serializer_to_database
from lib_core.utils import get_filenames_from_dir
from ressources.queryapi import Query
from ressources.reports import Report
from ultimate.ultimate_job import UltimateJob


def get_tag_by_name(jdb: JsonDatabase, name: str) -> Tag | None:
    for t in jdb.get_objects(Tag).values():
        if t.name == name:
            return t
    return None


def convert_pattern(old: OldPattern) -> Pattern:
    return Pattern(old.name)


def convert_scope(old: OldScope) -> Scope:
    match old:
        case OldScope.GLOBALLY:
            return Scope.GLOBALLY
        case OldScope.BEFORE:
            return Scope.BEFORE
        case OldScope.AFTER:
            return Scope.AFTER
        case OldScope.BETWEEN:
            return Scope.BETWEEN
        case OldScope.AFTER_UNTIL:
            return Scope.AFTER_UNTIL
        case _:
            return Scope.NONE


def convert_scoped_pattern(old: OldScopedPattern) -> ScopedPattern:
    if not old:
        return ScopedPattern(Scope.NONE, Pattern("NotFormalizable"))
    scope = convert_scope(old.scope)
    pattern = convert_pattern(old.pattern)
    scoped_pattern = ScopedPattern(scope, pattern)
    scoped_pattern.regex_pattern = old.regex_pattern
    return scoped_pattern


def convert_expression(old: OldExpression) -> Expression:
    expr: Expression = Expression(old.parent_rid)
    expr.used_variables = old.used_variables if old.used_variables else []
    expr.raw_expression = old.raw_expression
    return expr


def convert_formalization(old: OldFormalization) -> Formalization:
    if hasattr(old, "id"):
        f: Formalization = Formalization(old.id)
    else:
        f: Formalization = Formalization(0)
    f.scoped_pattern = convert_scoped_pattern(old.scoped_pattern)
    f.expressions_mapping = {
        e_name: convert_expression(expression) for e_name, expression in old.expressions_mapping.items()
    }
    if not hasattr(old, "type_inference_errors"):
        old.type_inference_errors = dict()
    f.type_inference_errors = old.type_inference_errors
    return f


def convert_requirement(no: int, old: OldRequirement, jdb: JsonDatabase, has_formalisation_tag: Tag) -> Requirement:
    # sanitize requirements name
    if not old.rid:
        old.rid = f"xreq_{no}"
    n_req: Requirement = Requirement(old.rid, old.description, old.type_in_csv, old.csv_row, old.pos_in_csv)
    n_req.formalizations = (
        {f_id: convert_formalization(f_value) for f_id, f_value in old.formalizations.items()}
        if isinstance(old.formalizations, dict)
        # catch if data is so old, that formalisations are stored in a list
        else {f_id: convert_formalization(f_value) for (f_id, f_value) in enumerate(old.formalizations)}
    )
    n_req.tags = {}
    if type(old.tags) is set:
        for t_name in old.tags:
            if t_name == "":
                continue
            tmp_tag = get_tag_by_name(jdb, t_name)
            if tmp_tag is None:
                tmp_tag = Tag(t_name, Color.BS_INFO.value, False, "")
            n_req.tags[tmp_tag] = ""
    else:
        for t_name, t_value in old.tags.items():
            if t_name == "":
                continue
            tmp_tag = get_tag_by_name(jdb, t_name)
            if tmp_tag is None:
                tmp_tag = Tag(t_name, Color.BS_INFO.value, False, "")
            n_req.tags[tmp_tag] = t_value
    if len(n_req.formalizations) > 0 and has_formalisation_tag not in n_req.tags:
        n_req.tags[has_formalisation_tag] = ""

    n_req.status = old.status
    if hasattr(old, "_revision_diff"):
        setattr(n_req, "_revision_diff", getattr(old, "_revision_diff"))
    return n_req


def convert_query(old: dict) -> Query:
    qry: Query = Query(old["name"], old["query"], old["result"])
    return qry


def convert_report(idx: int, old: dict) -> Report:
    report = Report(old["name"] if "name" in old else f"report_{idx}", old["queries"], old["results"])
    return report


def convert_ultimate_job(old: OldUltimateJob) -> UltimateJob:
    ultimate_job: UltimateJob = UltimateJob(
        job_id=old.job_id,
        requirement_file=old.requirement_file,
        toolchain_id=old.toolchain_id,
        toolchain_xml=old.toolchain_xml,
        usersettings_name=old.usersettings_name,
        usersettings_json=old.usersettings_json,
        selected_requirements=old.selected_requirements,
        results=old.results,
        result_requirements=old.result_requirements,
        api_url=old.api_url,
        job_status=old.job_status,
        request_time=datetime.strptime(old.request_time, "%Y.%m.%d, %H:%M:%S.%f"),
        last_update=datetime.strptime(old.last_update, "%Y.%m.%d, %H:%M:%S.%f"),
    )
    return ultimate_job


if __name__ == "__main__":
    HERE: str = path.dirname(path.realpath(__file__))

    # parse arguments
    parser = argparse.ArgumentParser(
        prog="Hanfor data migration", description="Migrates Hanfor data from pickle to json db."
    )
    parser.add_argument("base_folder")
    args = parser.parse_args()

    # move pickel folder and create new base folder
    if path.isabs(args.base_folder):
        base_folder: str = args.base_folder
    else:
        base_folder: str = path.join(HERE, args.base_folder)
    parts = base_folder.split(sep)
    parts[-1] = ".old_" + parts[-1]
    pickle_folder: str = sep.join(parts)
    move(base_folder, pickle_folder)
    mkdir(base_folder)

    names = listdir(pickle_folder)
    revisions = [name for name in names if path.isdir(path.join(pickle_folder, name)) and name.startswith("revision")]
    # for each revision
    for rev in revisions:
        revision_folder = path.join(pickle_folder, rev)

        # load meta_settings.pickle
        # -> Tags + colors
        # -> Queries
        # -> Reports
        old_meta_settings: dict = pickle_load_from_dump(path.join(pickle_folder, "meta_settings.pickle"))  # noqa

        # Ignore script_eval_results.pickle due to the deletion of the script eval functions.

        # load frontend_logs.pickle
        # -> RequirementEditHistory
        old_frontend_logs: dict = pickle_load_from_dump(path.join(pickle_folder, "frontend_logs.pickle"))  # noqa

        # load revisionXY/Requirements
        # -> Requirements
        old_requirements: set[OldRequirement] = set()
        for filename in get_filenames_from_dir(revision_folder):  # type: str
            if filename.endswith("session_status.pickle") or filename.endswith("session_variable_collection.pickle"):
                continue
            try:
                requirement = OldRequirement.load(filename)
                old_requirements.add(requirement)
            except TypeError as e:
                print(f"can not unpickle {filename}")
            except Exception as e:
                print(f"Unexpected exception:\n{e}")

        # load revisionXY/session_status.pickle
        # -> SessionValues
        session_dict: dict = pickle_load_from_dump(path.join(revision_folder, "session_status.pickle"))  # noqa

        # load revisionXY/session_variable_collection.pickle
        # -> Variables
        if path.isfile(path.join(revision_folder, "session_variable_collection.pickle")):
            old_var_collection = OldVariableCollection.load(
                path.join(revision_folder, "session_variable_collection.pickle")
            )
        else:
            old_var_collection = OldVariableCollection(path.join(revision_folder, "session_variable_collection.pickle"))

        # load revisionXY/ultimate_jobs
        ultimate_jobs: list[OldUltimateJob] = []
        if path.isdir(path.join(revision_folder, "ultimate_jobs")):
            for jf in get_filenames_from_dir(path.join(revision_folder, "ultimate_jobs")):
                ultimate_jobs.append(OldUltimateJob.from_file(file_name=jf))

        # --- NEW ---
        # create new Database
        db = JsonDatabase()
        add_custom_serializer_to_database(db)
        db.init_tables(path.join(base_folder, f"{rev}"))

        # insert SessionValues
        for k, v in session_dict.items():
            db.add_object(SessionValue(k, v))

        # insert Tags
        # tag_descriptions, tag_colors, tag_internal
        all_tags = set()
        if "tag_descriptions" in old_meta_settings:
            descriptions = old_meta_settings["tag_descriptions"]
            all_tags = all_tags.union(set(descriptions.keys()))
        else:
            descriptions = {}
        if "tag_colors" in old_meta_settings:
            colors = old_meta_settings["tag_colors"]
            all_tags = all_tags.union(set(colors.keys()))
        else:
            colors = {}
        if "tag_internal" in old_meta_settings:
            internal = old_meta_settings["tag_internal"]
            all_tags = all_tags.union(set(internal.keys()))
        else:
            internal = {}

        for tag_name in all_tags:
            if tag_name == "":
                continue
            color = colors.get(tag_name, Color.BS_INFO.value)
            inter = internal.get(tag_name, False)
            description = descriptions.get(tag_name, "")
            db.add_object(Tag(tag_name, color, inter, description))

        # insert Variables
        for name, var in old_var_collection.collection.items():
            v: Variable = Variable(var.name, var.type, var.value)
            if hasattr(var, "script_results"):
                v.script_results = var.script_results
            if hasattr(var, "belongs_to_enum"):
                v.belongs_to_enum = var.belongs_to_enum
            if hasattr(var, "description"):
                v.description = var.description
            if not hasattr(var, "tags"):
                # fix for old hanfor databases
                var.tags = set()
            for tag in var.tags:
                if not db.key_in_table(Tag, tag):
                    db.add_object(Tag(tag, Color.BS_INFO.value, False, ""))
                v.tags.add(get_tag_by_name(db, tag))
            if hasattr(var, "constraints"):
                for c_name, constraint in var.constraints.items():
                    v.constraints[c_name] = convert_formalization(constraint)
            db.add_object(v)

        # insert Requirements
        tag_has_formalisation = get_tag_by_name(db, "has_formalization")
        if not tag_has_formalisation:
            tag_has_formalisation = Tag("has_formalization", Color.BS_INFO.value, True, "")
            db.add_object(tag_has_formalisation)
        for i, old_req in enumerate(old_requirements):
            req = convert_requirement(i, old_req, db, tag_has_formalisation)
            db.add_object(req, delay_update=True)
        db.update()

        # insert RequirementEditHistory
        log_regex = re.compile(
            r"\[(?P<timestamp>.*?)] (?P<message>.*?) "
            r'(?P<references><a class="req_direct_link" href="#" data-rid=".*">.*</a>)+'
        )
        req_regex = re.compile(r'<a class="req_direct_link" href="#" data-rid="(?P<rid>.*?)">(?P=rid)</a>')
        if "hanfor_log" in old_frontend_logs:
            for log in old_frontend_logs["hanfor_log"]:
                try:
                    for match in log_regex.finditer(log):
                        timestamp = datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S.%f")
                        message = match.group("message")
                        rids = [rid.group("rid") for rid in req_regex.finditer(match.group("references"))]
                        db.add_object(
                            RequirementEditHistory(
                                timestamp, message, [db.get_object(Requirement, rid) for rid in rids]
                            )
                        )
                except DatabaseKeyError as e:
                    logging.warning(f"Unknown object in frontend log... skipping. ({e})")

        # insert Queries
        if "queries" in old_meta_settings:
            for _, q_value in old_meta_settings["queries"].items():
                db.add_object(convert_query(q_value))

        # insert Reports
        if "reports" in old_meta_settings:
            for i, r_value in enumerate(old_meta_settings["reports"]):
                db.add_object(convert_report(i, r_value))

        # insert UltimateJob
        for uj in ultimate_jobs:
            db.add_object(convert_ultimate_job(uj))
