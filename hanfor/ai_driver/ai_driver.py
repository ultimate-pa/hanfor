import logging
import hanfor.ai_driver.similarity_interface as sims
from reqtransformer import Requirement
import hanfor.ai_driver.ai_interface as ai_interface

global_db = None
cluster = None
debugEnabled = True


def initialize(db):
    global global_db
    global cluster
    global_db = db
    requirements = extract_requirements_from_db()
    cluster = sims.cluster_requirements_by_description(requirements)
    if debugEnabled:
        logging.debug(cluster)


# Get all Requirements from DB for clustering
def extract_requirements_from_db():
    try:
        reqs = global_db.get_objects(Requirement)
    except Exception as e:
        logging.error(f"Error loading requirements: {e}")
        return []

    if not reqs:
        logging.warning("No requirements found in the database.")
        return []

    requirements = []
    for key, requirement in reqs.items():
        try:
            req_type = requirement.csv_row.get("Type", None)
            if req_type == "requirement":
                requirements.append(
                    {
                        "id": requirement.csv_row.get("ID", "Unknown"),
                        "description": requirement.csv_row.get("Description", "No Description"),
                    }
                )
        except AttributeError as e:
            logging.error(f"Error accessing attributes of requirement {key}: {e}")
            continue
    if debugEnabled:
        logging.debug(requirements)
    return requirements


# Check whether the requirement is suitable for Ai formalization
def check_ai_formalization(rid: str) -> bool:
    req = global_db.get_object(Requirement, rid).to_dict(include_used_vars=True)
    if "has_formalization" in req["tags"]:
        return True
    return False


def update(rid: str):
    if not check_ai_formalization(rid):
        return

    updated_cluster = []
    req_without_formalization = False
    for cl in cluster:
        if rid in cl:
            for req_id in cl:
                req_data = global_db.get_object(Requirement, req_id).to_dict(include_used_vars=True)
                if not req_data["formal"]:
                    req_without_formalization = True
                    updated_cluster.append(req_data)
    if req_without_formalization:
        ai_interface.ai_formalization(
            global_db.get_object(Requirement, rid).to_dict(include_used_vars=True), updated_cluster
        )
    if debugEnabled:
        logging.debug(updated_cluster)
