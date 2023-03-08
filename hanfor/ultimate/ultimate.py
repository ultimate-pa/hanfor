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
        pass

    def get(self, command: str, job_id: str) -> str:
        if command == 'version':
            return self.ultimate.get_version()
        elif command == 'job':
            return self.ultimate.get_job(job_id)

    def post(self) -> str:
        return self.ultimate.start_job(
            "//#Unsafe\r\n//@+ltl+invariant+positive:+![](AP(chainBroken+==+1)+==>+[]AP(chainBroken+==+1));\r\n\r\n#include+<stdio.h>\r\n\r\nextern+void+__VERIFIER_error()+__attribute__+((__noreturn__));\r\nextern+void+__VERIFIER_assume()+__attribute__+((__noreturn__));\r\nextern+int+__VERIFIER_nondet_int()+__attribute__+((__noreturn__));\r\n\r\nint+error,+tempDisplay,+warnLED,+tempIn,+chainBroken,\r\nwarnLight,+temp,+limit,+init;\r\n\r\n\r\nvoid+display(int+tempdiff,+int+warning)\r\n{\r\n\ttempDisplay+=+tempdiff;\r\n\twarnLED+=+warning;\r\n}\r\n\r\nint+vinToCels(int+kelvin)\r\n{\r\n\tif+(temp+<+0)+\r\n\t{\r\n\t\terror+=+1;\r\n\t\tdisplay(kelvin+-+273,+error);\r\n\t}\r\n\treturn+kelvin+-273;\r\n}\r\n\r\nvoid+coolantControl()\r\n{\r\n\tint+otime,+time+=+0;\r\n\twhile(1)\r\n\t{\r\n\t\totime+=+time;\r\n\t\ttime+=+otime+++1;\r\n\t\ttempIn+=+__VERIFIER_nondet_int();\r\n\t\ttemp+=+vinToCels(tempIn);\r\n\t\tif(temp+>+limit)+\r\n\t\t{\r\n\t\t\tchainBroken+=+1;\r\n\t\t}+//else+{\r\n\t\t//\tchainBroken+=+0;\r\n\t\t//}\r\n\t}\r\n}\r\n\r\nint+main()\r\n{\r\n+init+=+0;\r\n++++tempDisplay+=+0;\r\n++++warnLED+=+1;\r\n++++tempIn+=+0;\r\n++++error+=+0;\r\n++++chainBroken+=+0;\r\n++++warnLight+=+0;\r\n++++temp+=+0;\r\n++++limit+=+8;\r\n++++init+=+1;\r\n++++int+try+=+0;\r\n\t\r\n\twhile(1)\r\n\t{\r\n\t\tint+limit+=+__VERIFIER_nondet_int();\r\n\t\tif(limit+<+10+&&+limit+>+-273)\r\n\t\t{\r\n\t\t\terror+=+0;\r\n\t\t\tdisplay(0,+error);\r\n\t\t\tbreak;\r\n\t\t}+else+{\r\n\t\t\terror+=+1;\r\n\t\t\tdisplay(0,+error);\r\n\t\t}\t\r\n\t\tif+(try+>=+3)+{\r\n\t\t\tlimit+=+7;\r\n\t\t\tbreak;\r\n\t\t}\r\n\t\ttry++;\r\n\t}\r\n\t\r\n\tinit+=+3;\r\n\tcoolantControl();\t\r\n}",
            "cLTLAutomizer",
            ".c",
            "{\"user_settings\":[{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\",\"default\":\"ASSUME\",\"visible\":false,\"name\":\"Pointer+base+address+is+valid+at+dereference\",\"options\":[\"IGNORE\",\"ASSUME\",\"ASSERTandASSUME\"],\"id\":\"cacsl2boogietranslator.pointer.base.address.is.valid.at.dereference\",\"type\":\"string\",\"key\":\"Pointer+base+address+is+valid+at+dereference\"},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\",\"default\":false,\"visible\":false,\"name\":\"Check+if+freed+pointer+was+valid\",\"id\":\"cacsl2boogietranslator.check.if.freed.pointer.was.valid\",\"type\":\"bool\",\"key\":\"Check+if+freed+pointer+was+valid\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\",\"default\":false,\"visible\":false,\"name\":\"Check+unreachability+of+error+function+in+SV-COMP+mode\",\"id\":\"cacsl2boogietranslator.check.unreachability.of.error.function.in.sv-comp.mode\",\"type\":\"bool\",\"key\":\"Check+unreachability+of+error+function+in+SV-COMP+mode\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\",\"default\":\"ASSUME\",\"visible\":false,\"name\":\"If+two+pointers+are+subtracted+or+compared+they+have+the+same+base+address\",\"options\":[\"IGNORE\",\"ASSUME\",\"ASSERTandASSUME\"],\"id\":\"cacsl2boogietranslator.if.two.pointers.are.subtracted.or.compared.they.have.the.same.base.address\",\"type\":\"string\",\"key\":\"If+two+pointers+are+subtracted+or+compared+they+have+the+same+base+address\"},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\",\"default\":\"ASSUME\",\"visible\":false,\"name\":\"Check+array+bounds+for+arrays+that+are+off+heap\",\"options\":[\"IGNORE\",\"ASSUME\",\"ASSERTandASSUME\"],\"id\":\"cacsl2boogietranslator.check.array.bounds.for.arrays.that.are.off.heap\",\"type\":\"string\",\"key\":\"Check+array+bounds+for+arrays+that+are+off+heap\"},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\",\"default\":true,\"visible\":false,\"name\":\"Use+constant+arrays\",\"id\":\"cacsl2boogietranslator.use.constant.arrays\",\"type\":\"bool\",\"key\":\"Use+constant+arrays\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\",\"default\":\"IGNORE\",\"visible\":false,\"name\":\"Check+division+by+zero\",\"options\":[\"IGNORE\",\"ASSUME\",\"ASSERTandASSUME\"],\"id\":\"cacsl2boogietranslator.check.division.by.zero\",\"type\":\"string\",\"key\":\"Check+division+by+zero\"},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\",\"default\":true,\"visible\":false,\"name\":\"Overapproximate+operations+on+floating+types\",\"id\":\"cacsl2boogietranslator.overapproximate.operations.on.floating.types\",\"type\":\"bool\",\"key\":\"Overapproximate+operations+on+floating+types\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\",\"default\":\"ASSUME\",\"visible\":false,\"name\":\"Pointer+to+allocated+memory+at+dereference\",\"options\":[\"IGNORE\",\"ASSUME\",\"ASSERTandASSUME\"],\"id\":\"cacsl2boogietranslator.pointer.to.allocated.memory.at.dereference\",\"type\":\"string\",\"key\":\"Pointer+to+allocated+memory+at+dereference\"},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.traceabstraction\",\"default\":\"CAMEL\",\"visible\":false,\"name\":\"Trace+refinement+strategy\",\"options\":[\"FIXED_PREFERENCES\",\"TAIPAN\",\"RUBBER_TAIPAN\",\"LAZY_TAIPAN\",\"TOOTHLESS_TAIPAN\",\"PENGUIN\",\"WALRUS\",\"CAMEL\",\"CAMEL_NO_AM\",\"CAMEL_SMT_AM\",\"LIZARD\",\"BADGER\",\"WOLF\",\"BEAR\",\"WARTHOG\",\"WARTHOG_NO_AM\",\"MAMMOTH\",\"MAMMOTH_NO_AM\",\"SMTINTERPOL\",\"DACHSHUND\",\"SIFA_TAIPAN\",\"TOOTHLESS_SIFA_TAIPAN\",\"MCR\"],\"id\":\"traceabstraction.trace.refinement.strategy\",\"type\":\"string\",\"key\":\"Trace+refinement+strategy\"},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.buchiautomizer\",\"default\":false,\"visible\":false,\"name\":\"Try+twofold+refinement\",\"id\":\"buchiautomizer.try.twofold.refinement\",\"type\":\"bool\",\"key\":\"Try+twofold+refinement\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.buchiautomizer\",\"default\":false,\"visible\":false,\"name\":\"Use+old+map+elimination\",\"id\":\"buchiautomizer.use.old.map.elimination\",\"type\":\"bool\",\"key\":\"Use+old+map+elimination\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.blockencoding\",\"default\":true,\"visible\":false,\"name\":\"Use+SBE\",\"id\":\"blockencoding.use.sbe\",\"type\":\"bool\",\"key\":\"Use+SBE\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.blockencoding\",\"default\":true,\"visible\":false,\"name\":\"Minimize+states+even+if+more+edges+are+added+than+removed.\",\"id\":\"blockencoding.minimize.states.even.if.more.edges.are.added.than.removed\",\"type\":\"bool\",\"key\":\"Minimize+states+even+if+more+edges+are+added+than+removed.\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.blockencoding\",\"default\":true,\"visible\":false,\"name\":\"Rewrite+not-equals\",\"id\":\"blockencoding.rewrite.not-equals\",\"type\":\"bool\",\"key\":\"Rewrite+not-equals\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.blockencoding\",\"default\":false,\"visible\":false,\"name\":\"Create+parallel+compositions+if+possible\",\"id\":\"blockencoding.create.parallel.compositions.if.possible\",\"type\":\"bool\",\"key\":\"Create+parallel+compositions+if+possible\",\"value\":false},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.blockencoding\",\"default\":\"NONE\",\"visible\":false,\"name\":\"Minimize+states+using+LBE+with+the+strategy\",\"options\":[\"NONE\",\"SINGLE\",\"SINGLE_NODE_MULTI_EDGE\",\"MULTI\"],\"id\":\"blockencoding.minimize.states.using.lbe.with.the.strategy\",\"type\":\"string\",\"key\":\"Minimize+states+using+LBE+with+the+strategy\"},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.plugins.generator.rcfgbuilder\",\"default\":\"SingleStatement\",\"visible\":false,\"name\":\"Size+of+a+code+block\",\"options\":[\"SingleStatement\",\"SequenceOfStatements\",\"LoopFreeBlock\"],\"id\":\"rcfgbuilder.size.of.a.code.block\",\"type\":\"string\",\"key\":\"Size+of+a+code+block\"},{\"plugin_id\":\"de.uni_freiburg.informatik.ultimate.core\",\"default\":\"de.uni_freiburg.informatik.ultimate.lib.smtlibutils.quantifier.QuantifierPusher=ERROR;\",\"visible\":false,\"name\":\"Log+level+for+class\",\"id\":\"core.log.level.for.class\",\"type\":\"string\",\"key\":\"Log+level+for+class\"}]}",
            "<rundefinition>\n<name>CLTLAutomizerTC</name>\n<toolchain>\n\t<plugin+id=\"de.uni_freiburg.informatik.ultimate.plugins.analysis.syntaxchecker\"/>\n\t<plugin+id=\"de.uni_freiburg.informatik.ultimate.plugins.generator.cacsl2boogietranslator\"/>\n\t<plugin+id=\"de.uni_freiburg.informatik.ultimate.boogie.preprocessor\"/>\n\t<plugin+id=\"de.uni_freiburg.informatik.ultimate.plugins.generator.rcfgbuilder\"/>\n\t<plugin+id=\"de.uni_freiburg.informatik.ultimate.plugins.generator.traceabstraction\"/>\n\t<plugin+id=\"de.uni_freiburg.informatik.ultimate.ltl2aut\"/>\n\t<plugin+id=\"de.uni_freiburg.informatik.ultimate.buchiprogramproduct\"/>\n\t<plugin+id=\"de.uni_freiburg.informatik.ultimate.plugins.blockencoding\"/>\n\t<plugin+id=\"de.uni_freiburg.informatik.ultimate.plugins.generator.buchiautomizer\"/>\n</toolchain></rundefinition>"
            )

    def delete(self, command: str, job_id: str) -> str:
        if command == 'job':
            return self.ultimate.delete_job(job_id)



register_api(api_blueprint, UltimateApi)
