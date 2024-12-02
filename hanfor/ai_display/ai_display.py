from typing import Type, Union
from flask import Blueprint, render_template, request, Response, jsonify
from flask.views import MethodView
from hanfor.ai_display.logic import ai_driver

# JavaScript bundle for the frontend
BUNDLE_JS = "dist/ai_display-bundle.js"

# Define the main blueprint for rendering the frontend
blueprint = Blueprint("ai_display", __name__, template_folder="templates", url_prefix="/ai_display")
# Define the blueprint for the API endpoints
api_blueprint = Blueprint("api_ai_display", __name__, url_prefix="/api/ai_display")


@blueprint.route("/", methods=["GET"])
def index():
    """Render the main page of the AI display."""
    return render_template("ai/index.html", BUNDLE_JS=BUNDLE_JS)


def register_api(bp: Blueprint, method_view: Type[MethodView]) -> None:
    """Register API routes with the given blueprint."""
    view = method_view.as_view("ai_api")
    bp.add_url_rule("/", defaults={"id": None}, view_func=view, methods=["GET"])
    bp.add_url_rule("/", view_func=view, methods=["POST"])
    bp.add_url_rule("/<int:id>", view_func=view, methods=["GET", "PUT", "PATCH", "DELETE"])


class AiApi(MethodView):
    """API class for handling clustering operations."""

    def post(self):
        """Handle POST requests for starting the clustering process."""
        data = request.get_json()

        if data.get("action") == "start_clustering":
            # Start the clustering process in a background thread
            ai_driver.start_clustering()
            return jsonify({"message": "Clustering started", "total": 10}), 200

        return jsonify({"error": "Invalid action"}), 400

    def get(self, id: int) -> Union[str, dict, tuple, Response]:
        """Handle GET requests to fetch clustering progress or cluster data."""
        query_type = request.args.get("type", "progress")

        if query_type == "progress":
            # Return the current progress state of the clustering process
            progress_state = ai_driver.get_progress_state_clustering()
            return jsonify(progress_state), 200
        elif query_type == "clusters":
            clusters = ai_driver.get_clusters()
            cluster_list = []
            if clusters is not None:
                for idx, cluster in enumerate(clusters):
                    cluster_list.append(
                        {
                            "name": f"Cluster {idx:02}",  # Format with leading zeros (e.g., "Cluster 00", "Cluster 01")
                            "ids": list(cluster),
                        }
                    )

            return jsonify({"clusters": cluster_list}), 200
        else:
            return jsonify({"error": "Invalid 'type' parameter"}), 400

    def put(self, id: int) -> Union[str, dict, tuple, Response]:
        """Handle PUT requests to create or fully update a resource."""
        return f"HTTP PUT request for id `{id}` received."

    def patch(self, id: int) -> Union[str, dict, tuple, Response]:
        """Handle PATCH requests to apply partial updates to a resource."""
        return f"HTTP PATCH request for id `{id}` received."

    def delete(self, id: int) -> Union[str, dict, tuple, Response]:
        """Handle DELETE requests to remove a specified resource."""
        return f"HTTP DELETE request for id `{id}` received."


# Register the API routes with the api_blueprint
register_api(api_blueprint, AiApi)


def update(rid: int) -> None:
    """Trigger the update process for a specific requirement ID."""
    ai_driver.update(rid)
