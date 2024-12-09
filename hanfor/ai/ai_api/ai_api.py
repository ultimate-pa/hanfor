import logging
import time

from flask import Blueprint, render_template, Response, jsonify, current_app
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


class ClusterApi(MethodView):
    def get(self):
        if current_app.ai.get_clusters():
            return jsonify([list(cluster) for cluster in current_app.ai.get_clusters()])
        return jsonify([])


class ClusterProgressApi(MethodView):
    def get(self) -> Response:
        return jsonify(current_app.ai.get_info())


class AiProgressApi(MethodView):
    def get(self):
        return jsonify(current_app.ai.get_ai_formalization_progress())


class TerminateAiApi(MethodView):
    def post(self):
        current_app.ai.terminate_ai_formalization_threads()
        return jsonify({"message": "AI process terminated."})


class TerminateClusteringApi(MethodView):
    def post(self):
        current_app.ai.terminate_cluster_thread()
        return jsonify({"message": "Clustering process terminated."})


class StartClusteringApi(MethodView):
    def post(self):
        current_app.ai.start_clustering()
        return jsonify({"message": "Clustering process started."})


# Register routes with their specific view classes
api_blueprint.add_url_rule("/cluster", view_func=ClusterApi.as_view("cluster"), methods=["GET"])
api_blueprint.add_url_rule(
    "/start_clustering", view_func=StartClusteringApi.as_view("start_clustering"), methods=["POST"]
)
api_blueprint.add_url_rule("/ai_progress", view_func=AiProgressApi.as_view("ai_progress"), methods=["GET"])
api_blueprint.add_url_rule(
    "/cluster_progress", view_func=ClusterProgressApi.as_view("cluster_progress"), methods=["GET"]
)
api_blueprint.add_url_rule("/terminate_ai", view_func=TerminateAiApi.as_view("terminate_ai"), methods=["POST"])
api_blueprint.add_url_rule(
    "/terminate_clustering", view_func=TerminateClusteringApi.as_view("terminate_clustering"), methods=["POST"]
)
