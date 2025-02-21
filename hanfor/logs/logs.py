from flask import Blueprint
from hanfor_flask import current_app, nocache, HanforFlask
from lib_core.data import RequirementEditHistory


api_blueprint = Blueprint("api_logs", __name__, url_prefix="/api/logs")


@api_blueprint.route("/get", methods=["GET"])
@nocache
def get_logs():
    return get_flask_session_log(current_app, html_format=True)


def get_flask_session_log(app: HanforFlask, html_format: bool = False) -> list | str:
    """Get the frontend log messages from frontend_logs.

    :param app: The flask app
    :param html_format: Return formatted html version.
    :return: list of messages or html string in case `html == True`
    """
    history_elements = app.db.get_objects(RequirementEditHistory)

    if html_format:
        result = ""
        for element in history_elements.values():  # type: RequirementEditHistory
            links = ",".join(
                [
                    ' <a class="req_direct_link" href="#" data-rid="{rid}">{rid}</a>'.format(rid=req.rid)
                    for req in element.requirements
                ]
            )
            result += f"<p>[{element.timestamp}] {element.message}{links}</p>"
    else:
        result = [history_elements.items()]

    return result
