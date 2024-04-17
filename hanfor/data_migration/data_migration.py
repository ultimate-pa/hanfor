# import new classes: SessionValues, Tags, Variables, Requirements, Queries, Reports, RequirementEditHistory

# from reqtransformer import Formalization, Requirement
import argparse
from os import path, sep, mkdir, listdir
from shutil import move

from static_utils import get_filenames_from_dir
from my_unpickler import pickle_load_from_dump, OldRequirement, OldVariableCollection, OldUltimateJob


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
    # pickle_folder: str = sep.join(parts)
    # move(base_folder, pickle_folder)
    # mkdir(base_folder)
    pickle_folder = base_folder

    names = listdir(pickle_folder)
    revisions = [name for name in names if path.isdir(path.join(pickle_folder, name)) and name.startswith("revision")]
    # for each revision
    for rev in revisions:
        revision_folder = path.join(pickle_folder, rev)

        # load meta_settings.pickle
        # -> Tags + colors
        # -> Queries
        # -> Reports
        old_meta_settings = pickle_load_from_dump(path.join(pickle_folder, "meta_settings.pickle"))

        # Ignore script_eval_results.pickle due to the deletion of the script eval functions.

        # load frontend_logs.pickle
        # -> RequirementEditHistory
        old_frontend_logs = pickle_load_from_dump(path.join(pickle_folder, "frontend_logs.pickle"))

        # load revisionXY/Requirements
        # -> Requirements
        # -> Tags ?
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
        session_dict = pickle_load_from_dump(path.join(revision_folder, "session_status.pickle"))

        # load revisionXY/session_variable_collection.pickle
        # -> Variables
        if path.isfile(path.join(revision_folder, "session_variable_collection.pickle")):
            old_var_collection = OldVariableCollection.load(
                path.join(revision_folder, "session_variable_collection.pickle")
            )
        else:
            old_var_collection = OldVariableCollection()

        # load revisionXY/ultimate_jobs
        ultimate_jobs: list[OldUltimateJob] = []
        if path.isdir(path.join(revision_folder, "ultimate_jobs")):
            for jf in get_filenames_from_dir(path.join(revision_folder, "ultimate_jobs")):
                ultimate_jobs.append(OldUltimateJob.from_file(file_name=jf))

        # --- NEW ---
        # create new Database

        # insert SessionValues

        # insert Tags

        # insert Variables

        # insert Requirements

        # insert Queries

        # insert Reports

        # insert RequirementEditHistory

        # insert UltimateJob
