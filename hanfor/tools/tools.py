import json

from flask import Blueprint, request, send_file

import utils
from hanfor_flask import current_app, nocache

api_blueprint = Blueprint("tools_api", __name__, url_prefix="/api/tools")


@api_blueprint.route("/<command>", methods=["GET", "POST"])
@nocache
def tools_api(command):
    filter_list = request.form.get("selected_requirement_ids", "")
    if len(filter_list) > 0:
        filter_list = json.loads(filter_list)
    else:
        filter_list = None

    file_name = f"{current_app.config['CSV_INPUT_FILE'][:-4]}"

    if command == "req_file":
        content = utils.generate_req_file_content(current_app, filter_list=filter_list)
        return utils.generate_file_response(content, file_name + ".req")

    if command == "csv_file":
        file = utils.generate_csv_file_content(current_app, filter_list=filter_list)
        name = f"{current_app.config['SESSION_TAG']}_{current_app.config['USING_REVISION']}_out.csv"
        return utils.generate_file_response(file, name, mimetype="text/csv")

    if command == "xls_file":
        file = utils.generate_xls_file_content(current_app, filter_list=filter_list)
        file.seek(0)
        return send_file(file, download_name=file_name + ".xlsx", as_attachment=True)
