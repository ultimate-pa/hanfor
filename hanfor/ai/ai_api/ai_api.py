import logging
from hanfor.ai.strategies.similarity_methods import sim_methods
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


class GetCurrentData(MethodView):
    def get(self) -> Response:
        return jsonify(current_app.ai.get_full_info())


class TerminateAll(MethodView):
    def post(self):
        current_app.ai.terminate_ai_formalization_threads()
        current_app.ai.terminate_cluster_thread()
        return jsonify({"message": "all processes terminated."})


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


class SetClusteringMethod(MethodView):
    def post(self):
        method_name = request.get_json().get("method_name")
        data = request.get_json().get("data")
        threshold = request.get_json().get("threshold", 0.8)  # Optional für Levenshtein

        # Die Methode anhand des Namens auswählen
        method = next((m for m in sim_methods if m["name"] == method_name), None)
        if method:
            result = (
                method["function"](data, threshold)
                if method_name == "Levenshtein Distance"
                else method["function"](data)
            )
            return jsonify({"message": f"{method_name} ausgeführt", "result": result})
        else:
            return jsonify({"error": "Unbekannte Methode"}), 400


class SetSimMethod(MethodView):
    def post(self):
        data = request.get_json()
        name = data.get("name")
        if name:
            current_app.ai.set_sim_methode(name)
            return jsonify({"message": f"Similarity method set to {name}."}), 200
        return jsonify({"error": "Method name is required."}), 400


class StartClustering(MethodView):
    def post(self):
        current_app.ai.start_clustering()
        return jsonify({"message": "Clustering process started."})


class TerminateSim(MethodView):
    def post(self):
        current_app.ai.terminate_cluster_thread()
        return jsonify({"message": "Clustering process terminated."})


class TerminateAi(MethodView):
    def post(self):
        current_app.ai.terminate_ai_formalization_threads()
        return jsonify({"message": "AI process terminated."})


class GetMatrix(MethodView):
    def get(self):
        return jsonify(current_app.ai.get_matrix())


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


# Register routes with their specific view classes
api_blueprint.add_url_rule("/get/current_data", view_func=GetCurrentData.as_view("get/current_data"), methods=["GET"])
api_blueprint.add_url_rule("/terminate/all", view_func=TerminateAll.as_view("terminate/all"), methods=["POST"])
api_blueprint.add_url_rule("/set/flag/system", view_func=SetSystemFlag.as_view("set/flag/system"), methods=["POST"])
api_blueprint.add_url_rule("/set/flag/ai", view_func=SetAiFlag.as_view("set/flag/ai"), methods=["POST"])
api_blueprint.add_url_rule("/set/method/sim", view_func=SetSimMethod.as_view("set/method/sim"), methods=["POST"])
api_blueprint.add_url_rule("/set/sim/start", view_func=StartClustering.as_view("sim/start"), methods=["POST"])
api_blueprint.add_url_rule("/terminate/sim", view_func=TerminateSim.as_view("terminate/sim"), methods=["POST"])
api_blueprint.add_url_rule("/get/sim/matrix", view_func=GetMatrix.as_view("sim/matrix"), methods=["GET"])
api_blueprint.add_url_rule("/terminate/ai", view_func=TerminateAi.as_view("terminate/ai"), methods=["POST"])
api_blueprint.add_url_rule("/ai/query", view_func=QueryAi.as_view("ai/query"), methods=["POST"])
api_blueprint.add_url_rule("/ai/process", view_func=ProcessAllReqAi.as_view("ai/process"), methods=["POST"])
