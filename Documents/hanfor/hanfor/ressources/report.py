from ressources import Ressource


class Report(Ressource):
    def __init__(self, app, request):
        super().__init__(app, request)
        if 'reports' not in self.meta_settings:
            self.meta_settings['reports'] = list()
            self.meta_settings.update_storage()

    @property
    def reports(self):
        return self.meta_settings['reports']

    def update_report(self, report_querys, report_results, report_id, name=''):
        """ Update a existing report. Create a new one if report_id < 0
        """
        if name == '':
                name = 'No {}'.format(len(self.meta_settings['reports'] if report_id < 0 else report_id))
        if report_id < 0:  # new report.
            self.meta_settings['reports'].append({'queries': report_querys, 'results': report_results, 'name': name})
        else:
            self.meta_settings['reports'][report_id] = {
                'queries': report_querys,
                'results': report_results,
                'name': name
            }
        self.meta_settings.update_storage()

    def GET(self):
        """ Fetch a list of all available reports.
        """
        self.response.data = self.reports

    def POST(self):
        report_querys = self.request.form.get('report_querys', '').strip()
        report_results = self.request.form.get('report_results', '').strip()
        report_id = int(self.request.form.get('report_id', '').strip())
        report_name = self.request.form.get('report_name', '').strip()
        self.update_report(report_querys, report_results, report_id, report_name)

    def DELETE(self):
        report_id = int(self.request.form.get('report_id', '').strip())
        self.meta_settings['reports'].pop(report_id)
        self.meta_settings.update_storage()
