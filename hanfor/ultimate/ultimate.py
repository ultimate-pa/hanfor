from typing import Type

from flask import Blueprint, render_template
from flask.views import MethodView

from ultimate.ultimate_connector import UltimateConnector

BUNDLE_JS = 'dist/ultimate-bundle.js'
blueprint = Blueprint('ultimate', __name__, template_folder='templates', url_prefix='/ultimate')
api_blueprint = Blueprint('api_ultimate', __name__, url_prefix='/api/ultimate')


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('ultimate/index.html', BUNDLE_JS=BUNDLE_JS)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    view = method_view.as_view('ultimate_api')
    bp.add_url_rule('/version',
                    defaults={'command': 'version', 'job_id': None},
                    view_func=view,
                    methods=['GET'])
    bp.add_url_rule('/job',
                    defaults={},
                    view_func=view,
                    methods=['POST'])
    bp.add_url_rule('/job/<string:job_id>',
                    defaults={'command': 'job'},
                    view_func=view,
                    methods=['GET', 'DELETE'])


class UltimateApi(MethodView):
    def __init__(self):
        self.ultimate = UltimateConnector

    def get(self, command: str, job_id: str) -> str:
        if command == 'version':
            return self.ultimate.get_version()
        elif command == 'job':
            return self.ultimate.get_job(job_id)

    def post(self) -> str:
        return self.ultimate.start_job(
            "//#Unsafe\r\n//@+ltl+invariant+positive:+![](AP(chainBroken+==+1)+==>+[]AP(chainBroken+==+1));\r\n\r\n#include+<stdio.h>\r\n\r\nextern+void+__VERIFIER_error()+__attribute__+((__noreturn__));\r\nextern+void+__VERIFIER_assume()+__attribute__+((__noreturn__));\r\nextern+int+__VERIFIER_nondet_int()+__attribute__+((__noreturn__));\r\n\r\nint+error,+tempDisplay,+warnLED,+tempIn,+chainBroken,\r\nwarnLight,+temp,+limit,+init;\r\n\r\n\r\nvoid+display(int+tempdiff,+int+warning)\r\n{\r\n\ttempDisplay+=+tempdiff;\r\n\twarnLED+=+warning;\r\n}\r\n\r\nint+vinToCels(int+kelvin)\r\n{\r\n\tif+(temp+<+0)+\r\n\t{\r\n\t\terror+=+1;\r\n\t\tdisplay(kelvin+-+273,+error);\r\n\t}\r\n\treturn+kelvin+-273;\r\n}\r\n\r\nvoid+coolantControl()\r\n{\r\n\tint+otime,+time+=+0;\r\n\twhile(1)\r\n\t{\r\n\t\totime+=+time;\r\n\t\ttime+=+otime+++1;\r\n\t\ttempIn+=+__VERIFIER_nondet_int();\r\n\t\ttemp+=+vinToCels(tempIn);\r\n\t\tif(temp+>+limit)+\r\n\t\t{\r\n\t\t\tchainBroken+=+1;\r\n\t\t}+//else+{\r\n\t\t//\tchainBroken+=+0;\r\n\t\t//}\r\n\t}\r\n}\r\n\r\nint+main()\r\n{\r\n+init+=+0;\r\n++++tempDisplay+=+0;\r\n++++warnLED+=+1;\r\n++++tempIn+=+0;\r\n++++error+=+0;\r\n++++chainBroken+=+0;\r\n++++warnLight+=+0;\r\n++++temp+=+0;\r\n++++limit+=+8;\r\n++++init+=+1;\r\n++++int+try+=+0;\r\n\t\r\n\twhile(1)\r\n\t{\r\n\t\tint+limit+=+__VERIFIER_nondet_int();\r\n\t\tif(limit+<+10+&&+limit+>+-273)\r\n\t\t{\r\n\t\t\terror+=+0;\r\n\t\t\tdisplay(0,+error);\r\n\t\t\tbreak;\r\n\t\t}+else+{\r\n\t\t\terror+=+1;\r\n\t\t\tdisplay(0,+error);\r\n\t\t}\t\r\n\t\tif+(try+>=+3)+{\r\n\t\t\tlimit+=+7;\r\n\t\t\tbreak;\r\n\t\t}\r\n\t\ttry++;\r\n\t}\r\n\t\r\n\tinit+=+3;\r\n\tcoolantControl();\t\r\n}",
            ".c",
            "cLTLAutomizer",
            ""
        )

    def delete(self, command: str, job_id: str) -> str:
        if command == 'job':
            return self.ultimate.delete_job(job_id)


register_api(api_blueprint, UltimateApi)
