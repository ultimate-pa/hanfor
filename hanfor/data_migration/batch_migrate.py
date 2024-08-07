import subprocess
from os import listdir
from os.path import isfile, join, isdir
from dataclasses import dataclass
import logging

"""
This script does a batch processing of a number of hanfor data directoies (tags)
into the new json-database format.  
To run this you will need a checkout of both, the old hanfor using the 
last version of the picle databse ()
and a checkout of the latest json-databse version containg the migration script.
"""

# Path containing pickle-databased hanfor (last version before jsondb) i.e. git-tag: TODO
OLD_HANFOR_PATH = r""
# Path to the version using the json database to run database update script
NEW_HANFOR_PATH = r""
# Path to directory in wich the to-be-batchprocessed old project are,
## must be the same as the data path of the two hanfor instances used here.
BATCH_PATH = r""

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class Project:
    tag: str
    revisions: list[str]


def get_projects(path: str) -> list[Project]:
    projects = []
    tags = [join(path, d) for d in listdir(path) if isdir(join(path, d))]
    for tag in tags:
        # TODO: only add if this is an onld thing, try figuring this out from file structure
        rev = [r for r in listdir(tag) if isdir(join(tag, r)) and r.startswith("revision_")]
        if not rev:
            logger.warning(f"No revisions were found for project {tag}")
            continue
        projects.append(Project(tag=tag, revisions=rev))
    return projects


def upgrade_picle_revision(project: Project, rev: int) -> bool:
    """Run old hanfor instance once to update project.
    Note: for simplicity, we just spin up the old hanfor version in a development server as its own proces"""
    logger.info(f"upgrading pickledatabase: '{project.tag}' ...")
    proc = subprocess.Popen(
        ["python", join(OLD_HANFOR_PATH, "app.py"), project.tag],
        cwd=OLD_HANFOR_PATH,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False,
    )
    error = False
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if line.startswith(b"Traceback"):
            error = True
        if line.startswith(b" * Running on"):
            logger.info(f"Hanfor started for '{project.tag}'! Killing Hanfor ...")
            proc.kill()
            return error
        if line.startswith(b"Which revision should I start."):
            logger.info(f"Selecting revision: {rev}")
            # detects if the revision choice is offered
            while True:
                line = proc.stdout.readline()
                # detects _the end of the revision choice_ box, and
                # does the correct choice immediately (before process locks)
                if line.startswith(b"\xe2\x95\x9a\xe2"):
                    proc.stdin.write(f"{rev}\n".encode())
                    proc.stdin.flush()
                    break
        if error:
            logger.error(
                f"HANFOR::: {line.decode()[0:-2]}",
            )
    return error


def upgrade_to_json(project: Project) -> bool:
    logger.info(f"upgrading to json: '{project.tag}' ...")
    proc = subprocess.Popen(
        ["python", "-m", "hanfor.data_migration.data_migration", project.tag],
        cwd=NEW_HANFOR_PATH,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False,
    )
    error = False
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if line.startswith(b"Traceback"):
            error = True
        if error:
            logger.error(f"TRANSLATOR::: {line.decode()[0:-2]}")
        else:
            logger.info(f"TRANSLATOR::: {line.decode()[0:-2]}")
    return error


def verify_upgrade(project: Project, rev: int) -> bool:
    """Run old hanfor instance once to update project.
    Note: for simplicity, we just spin up the old hanfor version in a development server as its own proces"""
    logger.info(f"verifying that json update is loadable: '{project.tag}' at revision '{rev}' ...")
    proc = subprocess.Popen(
        ["python", join(NEW_HANFOR_PATH, "app.py"), project.tag],
        cwd=NEW_HANFOR_PATH,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False,
    )
    error = False
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if line.startswith(b"Traceback"):
            error = True
        if line.startswith(b" * Running on"):
            logger.info(f"Hanfor started for '{project.tag}' at '{rev}'! Everythin seems to be fine   \o/")
            proc.kill()
            return error
        if line.startswith(b"Which revision should I start."):
            logger.info(f"Selecting revision: {rev}")
            # detects if the revision choice is offered
            while True:
                line = proc.stdout.readline()
                # detects _the end of the revision choice_ box, and
                # does the correct choice immediately (before process locks)
                if line.startswith(b"\xe2\x95\x9a\xe2"):
                    proc.stdin.write(f"{rev}\n".encode())
                    proc.stdin.flush()
                    break
        if error:
            logger.error(
                f"HANFOR::: {line.decode()[0:-2]}",
            )
    return error


def upgrade_project(project: Project):
    # update old pickle revisions
    logging.info("##############################################")
    logging.info(f"### {project.tag}")
    logging.info("##############################################")
    for i, rev in enumerate(project.revisions):
        if upgrade_picle_revision(project, i):
            return
    if upgrade_to_json(project):
        return
    for i, rev in enumerate(project.revisions):
        if verify_upgrade(project, i):
            return


def main():
    logger.info(f"Analysing {BATCH_PATH}")
    projects = get_projects(BATCH_PATH)
    for project in projects:
        upgrade_project(project)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
