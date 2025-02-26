from ressources.ressource import Ressource
from dataclasses import dataclass, field
from json_db_connector.json_db import DatabaseTable, TableType, DatabaseID, DatabaseField
from uuid import uuid4


@DatabaseTable(TableType.Folder)
@DatabaseID("id", use_uuid=True)
@DatabaseField("name", str)
@DatabaseField("queries", str)
@DatabaseField("results", str)
@dataclass()
class Report:
    name: str
    queries: str
    results: str
    id: str = field(default_factory=lambda: str(uuid4()))  # TODO: id is set but never used

    def get_dict(self) -> dict[str, str]:
        return {"name": self.name, "queries": self.queries, "results": self.results}


class Reports(Ressource):
    def __init__(self, app, request):
        super().__init__(app, request)

    @property
    def reports(self):
        return [r.get_dict() for r in self.app.db.get_objects(Report).values()]

    def update_report(self, queries, results, report_id, name=""):
        """Update an existing report. Create a new one if report_id < 0"""
        if not self.app.db.key_in_table(Report, report_id):  # catch unknown id -> new report
            report_id = -1
        next_id = 0
        while self.app.db.key_in_table(Report, next_id):
            next_id += 1
        if name == "":
            name = "No {}".format(next_id if report_id < 0 else report_id)
        if report_id < 0:  # new report.
            self.app.db.add_object(Report(name, queries, results))
        else:
            report = self.app.db.get_object(Report, report_id)
            report.name = name
            report.queries = queries
            report.results = results
            self.app.db.update()

    def GET(self):
        """Fetch a list of all available reports."""
        self.response.data = self.reports

    def POST(self):
        report_queries = self.request.form.get("report_querys", "").strip()
        report_results = self.request.form.get("report_results", "").strip()
        report_id = int(self.request.form.get("report_id", "").strip())
        report_name = self.request.form.get("report_name", "").strip()
        self.update_report(report_queries, report_results, report_id, report_name)

    def DELETE(self):
        report_id = int(self.request.form.get("report_id", "").strip())
        report = self.app.db.get_object(Report, report_id)
        self.app.db.remove_object(report)
