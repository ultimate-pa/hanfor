from ressources import Ressource
from utils import MetaSettings


class Report(Ressource):
    def __init__(self, app, request):
        super().__init__(app, request)
        meta_settings = self.get_meta_settings()
        if 'reports' not in meta_settings:
            meta_settings['reports'] = list()
            meta_settings.update_storage()

    @property
    def reports(self):
        meta_settings = self.get_meta_settings()
        return meta_settings['reports']

    def update_report(self, report_querys, report_results, report_id):
        meta_settings = self.get_meta_settings()
        if report_id < 0:  # new report.
            meta_settings['reports'].append({'queries': report_querys, 'results': report_results})
        else:
            meta_settings['reports'][report_id] = {'queries': report_querys, 'results': report_results}
        meta_settings.update_storage()

    def GET(self):
        """ Fetch a list of all available reports.
        """
        self.response.data = self.reports

    def POST(self):
        report_querys = self.request.form.get('report_querys', '').strip()
        report_results = self.request.form.get('report_results', '').strip()
        report_id = int(self.request.form.get('report_id', '').strip())
        self.update_report(report_querys, report_results, report_id)

    def DELETE(self):
        report_id = int(self.request.form.get('report_id', '').strip())
        meta_settings = self.get_meta_settings()
        meta_settings['reports'].pop(report_id)
        meta_settings.update_storage()
