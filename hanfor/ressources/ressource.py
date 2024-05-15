from flask import jsonify
from hanfor_flask import HanforFlask


class Ressource:
    def __init__(self, app: HanforFlask, request):
        self.app = app
        self.request = request
        self.response = Response()

    def apply_request(self):
        getattr(self, self.request.method)()
        return jsonify(self.response), self.response.http_status

    def GET(self):  # noqa
        raise NotImplementedError

    def POST(self):  # noqa
        raise NotImplementedError

    def DELETE(self):  # noqa
        raise NotImplementedError


class Response(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["success"] = True
        self["errormsg"] = ""
        self["HTTP_status"] = 200

    @property
    def success(self):
        return self["success"]

    @success.setter
    def success(self, val):
        if not val and len(self.errormsg) == 0:
            self["errormsg"] = "Sorry, could not parse your request."
        self["success"] = val

    @property
    def http_status(self):
        return self["HTTP_status"]

    @http_status.setter
    def http_status(self, code):
        self["HTTP_status"] = code

    @property
    def errormsg(self):
        return self["errormsg"]

    @errormsg.setter
    def errormsg(self, msg):
        self["errormsg"] = msg

    @property
    def data(self):
        return self["data"]

    @data.setter
    def data(self, data):
        self["data"] = data
