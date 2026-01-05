""" 

@copyright: 2018 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""

import csv
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from hanfor_flask import HanforFlask
from configuration.defaults import Color
from lib_core.data import Requirement, Formalization, Tag, VariableCollection, Variable, SessionValue
from lib_core.utils import choice


@dataclass
class CsvConfig:
    """Representation of structure of csv being imported"""

    dialect: str = None
    fieldnames: str = None
    headers: list = field(default_factory=list)
    id_header: str = None
    desc_header: str = None
    formal_header: str = None
    type_header: str = None
    tags_header: str = None
    status_header: str = None
    import_formalizations: bool = False


class RequirementCollection:

    def __init__(self):
        self.csv_meta = CsvConfig()
        self.csv_all_rows = None
        self.requirements = list()

    def create_from_csv(
        self,
        csv_file,
        app,
        input_encoding="utf8",
        base_revision_headers=None,
        user_provided_headers=None,
        available_sessions=None,
    ):
        """Create a RequirementCollection from a csv file, containing one requirement per line.
        Ask the user which csv fields corresponds to which requirement data.

        Args:
            csv_file (str):
            app (Flask.app):
            input_encoding (str):
            base_revision_headers (dict):
            user_provided_headers (dict):
            available_sessions (tuple):
        """
        self.load_csv(csv_file, input_encoding)
        self.select_headers(base_revision_headers=base_revision_headers, user_provided_headers=user_provided_headers)
        self.process_csv_hanfor_data_import(available_sessions=available_sessions, app=app)
        self.parse_csv_rows_into_requirements(app)

    def load_csv(self, csv_file: str, input_encoding: str):
        """Reads a csv file into `csv_all_rows`. Stores csv_dialect and csv_fieldnames in `csv_meta`

        :param csv_file: Path to csv file.
        :param input_encoding: Encoding of the csv file.
        """
        logging.info(f"Load Input : {csv_file}")
        with open(csv_file, "r", encoding=input_encoding) as csvfile:
            csv.register_dialect("ultimate", delimiter=",", escapechar="\\", quoting=csv.QUOTE_ALL, quotechar='"')
            dialect = "ultimate"
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect, restkey="CSV-None")
            self.csv_all_rows = list(reader)
            self.csv_meta.fieldnames = reader.fieldnames
            self.csv_meta.headers = sorted(list(reader.fieldnames))

    def select_headers(self, base_revision_headers=None, user_provided_headers=None):
        """Determines which of the csv headers correspond to our needed data.

        Args:
            base_revision_headers:
            user_provided_headers:
        """
        use_old_headers = False
        if base_revision_headers:
            print("Should I use the csv header mapping from base revision?")
            use_old_headers = choice(["yes", "no"], "yes")

        if user_provided_headers:
            print(user_provided_headers)
            self.csv_meta.id_header = user_provided_headers["csv_id_header"]
            self.csv_meta.desc_header = user_provided_headers["csv_desc_header"]
            self.csv_meta.formal_header = user_provided_headers["csv_formal_header"]
            self.csv_meta.type_header = user_provided_headers["csv_type_header"]
        elif base_revision_headers and use_old_headers == "yes":
            self.csv_meta.id_header = base_revision_headers["csv_id_header"].value
            self.csv_meta.desc_header = base_revision_headers["csv_desc_header"].value
            self.csv_meta.formal_header = base_revision_headers["csv_formal_header"].value
            self.csv_meta.type_header = base_revision_headers["csv_type_header"].value
        else:
            available_headers = set(self.csv_meta.headers)
            available_headers.discard("Hanfor_Tags")
            available_headers.discard("Hanfor_Status")
            available_headers = sorted(available_headers)

            print("Select ID header")
            self.csv_meta.id_header = choice(available_headers, "ID")
            print("Select requirements description header")
            self.csv_meta.desc_header = choice(available_headers, "Object Text")
            print("Select formalization header")
            self.csv_meta.formal_header = choice(available_headers + ["Add new Formalization"], "Hanfor_Formalization")
            if self.csv_meta.formal_header == "Add new Formalization":
                self.csv_meta.formal_header = "Hanfor_Formalization"
            print("Select type header.")
            self.csv_meta.type_header = choice(available_headers, "RB_Classification")

    def process_csv_hanfor_data_import(self, available_sessions, app):
        if app.config["USING_REVISION"] != "revision_0":  # We only support importing formalizations for base revisions
            return

        print("Do you want to import existing data from CSV?")
        if choice(["no", "yes"], "no") == "no":
            return

        print("Do you want to import Formalizations from CSV?")
        import_formalizations = choice(["no", "yes"], "no")
        if import_formalizations == "yes":
            self.csv_meta.import_formalizations = True

        print("Do you want to import Hanfor tags and status from CSV?")
        if choice(["no", "yes"], "no") == "yes":
            print("Select the Hanfor Tags header.")
            self.csv_meta.tags_header = choice(self.csv_meta.headers, "Hanfor_Tags")
            print("Select the Hanfor Status header.")
            self.csv_meta.status_header = choice(self.csv_meta.headers, "Hanfor_Status")

        print("Do you want to import a base Variable collection?")
        if choice(["no", "yes"], "yes") == "yes":
            available_sessions = [s for s in available_sessions]
            available_sessions_names = [s["name"] for s in available_sessions]
            if len(available_sessions_names) > 0:
                print("Choose the Variable Collection to import.")
                chosen_session = choice(available_sessions_names, available_sessions_names[0])
                print("Choose the revision for session {}".format(chosen_session))
                available_revisions = [
                    r for r in available_sessions[available_sessions_names.index(chosen_session)]["revisions"]
                ]
                # TODO: here there is funky stuff with revision choice
                # revision_choice = choice(available_revisions, available_revisions[0])
                # imported_var_collection = VariableCollection.load(
                #     os.path.join(
                #         app.config["SESSION_BASE_FOLDER"],
                #         chosen_session,
                #         revision_choice,
                #         "session_variable_collection.pickle",
                #     )
                # )
                # imported_var_collection.store(app.config["SESSION_VARIABLE_COLLECTION"])
            else:
                print("No sessions available. Skipping")

    def parse_csv_rows_into_requirements(self, app: HanforFlask):
        """Parse each row in csv_all_rows into one Requirement.

        Args:
            app (Flask): Hanfor Flask app.

        """
        for index, row in enumerate(self.csv_all_rows):
            # Todo: Use utils.slugify to make the rid save for a filename.
            requirement = Requirement(
                rid=row[self.csv_meta.id_header],
                description=try_cast_string(row[self.csv_meta.desc_header]),
                type_in_csv=try_cast_string(row[self.csv_meta.type_header]),
                csv_row=row,
                pos_in_csv=index,
            )
            variable_collection = VariableCollection(
                app.db.get_objects(Variable).values(), app.db.get_objects(Requirement).values()
            )
            if self.csv_meta.import_formalizations:
                # Set the tags
                if self.csv_meta.tags_header is not None:
                    all_tags: dict[str, Tag] = {t.name: t for t in app.db.get_objects(Tag).values()}
                    for t in row[self.csv_meta.tags_header].split(","):
                        if t not in all_tags:
                            tag = Tag(t, Color.BS_INFO.value, False, "")
                            app.db.add_object(tag)
                        else:
                            tag = all_tags[t]
                        requirement.tags[tag] = ""
                # Set the status
                if self.csv_meta.status_header is not None:
                    status = row[self.csv_meta.status_header].strip()
                    if status not in ["Todo", "Review", "Done"]:
                        logging.debug("Status {} not supported. Set to `Todo`".format(status))
                        status = "Todo"
                    requirement.status = status
                # Parse and set the requirements.
                formalizations = json.loads(row[self.csv_meta.formal_header])
                for key, formalization_dict in formalizations.items():
                    formalization = Formalization(int(key))
                    requirement.formalizations[int(key)] = formalization
                    requirement.update_formalization(
                        formalization_id=int(key),
                        scope_name=formalization_dict["scope"],
                        pattern_name=formalization_dict["pattern"],
                        mapping=formalization_dict["expressions"],
                        variable_collection=variable_collection,
                        standard_tags=SessionValue.get_standard_tags(app.db),
                    )
            for v in variable_collection.new_vars:
                app.db.add_object(v)
            self.requirements.append(requirement)


def try_cast_string(data: Any) -> str:
    try:
        return str(data)
    except TypeError as e:
        logging.warning(f"Failed string cast:\n {e}")
    return "CSV-None"
