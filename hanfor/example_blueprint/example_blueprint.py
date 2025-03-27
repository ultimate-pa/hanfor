import json
from flask import Blueprint, render_template, request
from flask_restx import Resource, Namespace, fields
from lib_core.api_models import ExampleBlueprintUser, ExampleBlueprintUsers, ExampleBluprintNames


# To generate a ...-bundle.js file for the frontend add an entry to the `/static/webpack.config.js` at `config - entry`
# with the name of the module and the path to the js file
BUNDLE_JS = "dist/example_blueprint-bundle.js"
# Define the frontend blueprint for the model
blueprint = Blueprint("example-blueprint", __name__, template_folder="templates", url_prefix="/example-blueprint")

# Define the api namespace for the model
api = Namespace("Example Blueprint", "Example Blueprint Description", path="/example-blueprint", ordered=True)

# Just some example data
example_data = {
    0: {"name": "Alice", "age": 42, "city": "Augsburg"},
    1: {"name": "Bob", "age": 40, "city": "Berlin"},
    2: {"name": "Clarice", "age": 44, "city": "Cottbus"},
    3: {"name": "Dave", "age": 39, "city": "Dresden"},
}


# Define all frontend endpoints
@blueprint.route("/", methods=["GET"])
def index():
    # To get the url for an endpoint at a html blueprint use `url_for('[blueprint_name].[function_name]')`,
    # e.g., `url_for('ultimate.index')`
    # All html blueprint of a module should be in the folder `module/templates/[module_name]/`
    # To hand over variables to the html blueprint just add them with a unique name at the end,
    # e.g., provide the string BUNDLE_JS as BUNDLE_JS
    return render_template("example_blueprint/index.html", BUNDLE_JS=BUNDLE_JS)


# Define all api endpoints
# All api endpoints should follow this guidelines:
# GET: for requesting one/multiple item
# DELETE: delete one item
# PUT: - create a new item with the given id
#      - override the item with the given id
# POST: - create new item without id: return the id of the new item
#       - miscellaneous request like performing a function on all items without any parameters
# PATCH: make partial changes on item with the given id
@api.route("/")
class ApiExampleBlueprintItems(Resource):
    @api.response(200, "Success", ExampleBlueprintUsers)
    def get(self):
        """Get all users"""
        return {"data": example_data}

    @api.expect(ExampleBlueprintUser)
    @api.response(200, "Success", fields.Integer)
    @api.response(400, "Bad Request")
    def post(self):
        """Create user"""
        data = json.loads(request.get_data())
        if "name" in data and "age" in data and "city" in data:
            if len(example_data) == 0:
                next_id = 0
            else:
                next_id = max(example_data.keys()) + 1
            example_data[next_id] = {"name": data["name"], "age": data["age"], "city": data["city"]}
            return next_id
        return None, 400


@api.route("/<int:example_id>")
class ApiExampleBlueprintItem(Resource):
    @api.doc(
        description="Get user with example_id",
        params={
            "example_id": {"description": "The ID of the user", "required": True},
        },
    )
    @api.response(200, "Success", ExampleBlueprintUser)
    @api.response(404, "Not Found")
    def get(self, example_id: int):
        """Get the number as string"""
        if example_id in example_data:
            return example_data[example_id]
        return {}, 404

    @api.doc(
        params={
            "example_id": {"description": "The ID of the Example", "required": True},
        },
    )
    @api.response(200, "Success")
    @api.response(404, "Not Found")
    def delete(self, example_id: int):
        """Delete the user with id: example:id"""
        if example_id in example_data:
            del example_data[example_id]
            return None, 200
        return None, 404

    @api.doc(
        params={
            "example_id": {"description": "The ID of the user", "required": True},
        },
    )
    @api.expect(ExampleBlueprintUser)
    @api.response(200, "Success", ExampleBlueprintUser)
    @api.response(400, "Bad Request")
    def put(self, example_id: int):
        """Override or create user"""
        data = json.loads(request.get_data())
        if "name" in data and "age" in data and "city" in data:
            example_data[example_id] = {"name": data["name"], "age": data["age"], "city": data["city"]}
            return example_data[example_id]
        return None, 400

    @api.doc(
        params={
            "example_id": {"description": "The ID of the Example", "required": True},
        },
    )
    @api.expect(ExampleBlueprintUser)
    @api.response(200, "Success", ExampleBlueprintUser)
    @api.response(404, "Not Found")
    @api.response(400, "Bad Request")
    def patch(self, example_id: int):
        """Make partial changes to user"""
        if example_id not in example_data:
            return None, 404
        changes = False
        data = json.loads(request.get_data())
        if "name" in data:
            example_data[example_id]["name"] = data["name"]
            changes = True
        if "age" in data:
            example_data[example_id]["age"] = data["age"]
            changes = True
        if "city" in data:
            example_data[example_id]["city"] = data["city"]
            changes = True
        if changes:
            return example_data[example_id]
        return None, 400


@api.route("/names")
class ApiExampleBlueprintNames(Resource):
    @api.response(200, "Success", ExampleBluprintNames)
    def get(self):
        """Get all users name"""
        names = [user["name"] for user in example_data.values()]
        return {"names": names}
