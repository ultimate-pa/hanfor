from flask import Blueprint, render_template, Response, jsonify, current_app, request
from flask.views import MethodView

# JavaScript bundle for the frontend
BUNDLE_JS = "dist/ai-bundle.js"

# Define the main blueprint for rendering the frontend
blueprint = Blueprint("ai", __name__, template_folder="templates", url_prefix="/ai")
# Define the blueprint for the API endpoints
api_blueprint = Blueprint("api_ai", __name__, url_prefix="/api/ai")


@blueprint.route("/", methods=["GET"])
def index():
    """Render the main page of the AI display."""
    return render_template("ai_html/index.html", BUNDLE_JS=BUNDLE_JS)


class GetFullInitialData(MethodView):
    def get(self) -> Response:
        return jsonify(current_app.ai.get_full_info_init_site())


# region Terminate
class TerminateAll(MethodView):
    def post(self):
        current_app.ai.terminate_cluster_thread()
        current_app.ai.terminate_ai_formalization_threads()
        return jsonify({"message": "all processes terminated."})


class TerminateSim(MethodView):
    def post(self):
        current_app.ai.terminate_cluster_thread()
        return jsonify({"message": "Clustering process terminated."})


class TerminateAi(MethodView):
    def post(self):
        current_app.ai.terminate_ai_formalization_threads()
        return jsonify({"message": "AI process terminated."})


# endregion


# region Flags
class SetSystemFlag(MethodView):
    def post(self):
        system_enabled = request.get_json().get("system_enabled", False)
        current_app.ai.set_flag_system(system_enabled)
        return jsonify({"message": f"System status set to {'enabled' if system_enabled else 'disabled'}."})


class SetAiFlag(MethodView):
    def post(self):
        ai_enabled = request.get_json().get("ai_enabled", False)
        current_app.ai.set_flag_ai(ai_enabled)
        return jsonify({"message": f"System status set to {'enabled' if ai_enabled else 'disabled'}."})


# endregion


# region Clustering
class SetSimMethod(MethodView):
    def post(self):
        data = request.get_json()
        name = data.get("name")
        if name:
            current_app.ai.set_sim_methode(name)
            return jsonify({"message": f"Similarity method set to {name}."}), 200
        return jsonify({"error": "Method name is required."}), 400


class SetSimThreshold(MethodView):
    def post(self):
        data = request.get_json()
        threshold = float(data.get("threshold"))
        current_app.ai.set_sim_threshold(threshold)
        return jsonify({"message": "threshold set to {threshold}."}), 200


class StartClustering(MethodView):
    def post(self):
        current_app.ai.start_clustering()
        return jsonify({"message": "Clustering process started."})


class GetMatrix(MethodView):
    def get(self):
        return jsonify(current_app.ai.get_matrix())


# endregion


# region Ai
class QueryAi(MethodView):
    def post(self):
        data = request.get_json()
        query = data.get("query")
        if not query:
            return jsonify({"error": "No query provided"}), 400
        current_app.ai.query_ai(query)
        return jsonify({"status": "processing"}), 202


class ProcessAllReqAi(MethodView):
    def post(self):
        current_app.ai.check_for_process()
        return jsonify({"message": "Checking for Process."})


class SetAiMethod(MethodView):
    def post(self):
        data = request.get_json()
        name = data.get("name")
        if name:
            current_app.ai.set_ai_methode(name)
            return jsonify({"message": f"Similarity method set to {name}."}), 200
        return jsonify({"error": "Method name is required."}), 400


class SetAiModel(MethodView):
    def post(self):
        data = request.get_json()
        name = data.get("name")
        if name:
            current_app.ai.set_ai_model(name)
            return jsonify({"message": f"Similarity method set to {name}."}), 200
        return jsonify({"error": "Method name is required."}), 400


# endregion


# region chosen Requirement Ai formalization
class SetIds(MethodView):
    def post(self):
        data = request.get_json()
        ids = data.get("ids")
        if ids:
            e = current_app.ai.update_ids(ids)
            if not e:
                return jsonify({"message": f"set ids: {ids}."}), 200
            return jsonify({"error": str(e)}), 400


# endregion

# region Log from Requirements


class GetLogFromId(MethodView):
    def get(self):
        id = request.args.get("id")
        if id:
            log_data = current_app.ai.get_log_from_id(id)
            if log_data:
                return jsonify({"message": f"ID found: {id}", "data": log_data}), 200
            else:
                return jsonify({"error": f"No data for ID {id} found"}), 404
        return jsonify({"error": "No ID"}), 400


# endregion

# region Register routes
api_blueprint.add_url_rule(
    "/get/data/initial", view_func=GetFullInitialData.as_view("get/data/initial"), methods=["GET"]
)
api_blueprint.add_url_rule("/get/sim/matrix", view_func=GetMatrix.as_view("sim/matrix"), methods=["GET"])

api_blueprint.add_url_rule("/set/log/id", view_func=GetLogFromId.as_view("set/log/id"), methods=["GET"])

api_blueprint.add_url_rule("/terminate/all", view_func=TerminateAll.as_view("terminate/all"), methods=["POST"])
api_blueprint.add_url_rule("/terminate/sim", view_func=TerminateSim.as_view("terminate/sim"), methods=["POST"])
api_blueprint.add_url_rule("/terminate/ai", view_func=TerminateAi.as_view("terminate/ai"), methods=["POST"])

api_blueprint.add_url_rule("/set/flag/system", view_func=SetSystemFlag.as_view("set/flag/system"), methods=["POST"])
api_blueprint.add_url_rule("/set/flag/ai", view_func=SetAiFlag.as_view("set/flag/ai"), methods=["POST"])

api_blueprint.add_url_rule("/set/sim/method", view_func=SetSimMethod.as_view("set/sim/method"), methods=["POST"])
api_blueprint.add_url_rule("/set/sim/start", view_func=StartClustering.as_view("sim/start"), methods=["POST"])
api_blueprint.add_url_rule("/set/sim/threshold", view_func=SetSimThreshold.as_view("sim/threshold"), methods=["POST"])

api_blueprint.add_url_rule("/ai/query", view_func=QueryAi.as_view("ai/query"), methods=["POST"])
api_blueprint.add_url_rule("/ai/process", view_func=ProcessAllReqAi.as_view("ai/process"), methods=["POST"])

api_blueprint.add_url_rule("/set/ai/method", view_func=SetAiMethod.as_view("set/ai/method"), methods=["POST"])
api_blueprint.add_url_rule("/set/ai/model", view_func=SetAiModel.as_view("set/ai/model"), methods=["POST"])
api_blueprint.add_url_rule("/set/ids", view_func=SetIds.as_view("set/ids"), methods=["POST"])

# endregion
