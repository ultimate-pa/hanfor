from flask_restx import fields, Namespace
from flask_restx.fields import Nested

api_models = Namespace("API Models", description="API Models Namespace")

# Example Blueprint Models
# A model is only displayed in the swagger documentation if it is used by at least one registered api endpoint.
# The values in parentheses of fields.String/Integer/Bool as default/example values
ExampleBlueprintUser = api_models.model(
    "Example User", {"name": fields.String("Erin"), "age": fields.Integer(31), "city": fields.String("Erfurt")}
)
# use fields.Wildcard to generate dictionaries with unknown keys, e.g., data is a dict containing user_id: user_data
# use fields.Nested to use another model inside a model
ExampleBlueprintUsers = api_models.model(
    "Example User List", {"data": fields.Wildcard(fields.Nested(ExampleBlueprintUser))}
)
# To add an example to fields.List/Wildcard use the named parameter example
ExampleBluprintNames = api_models.model(
    "Example Names", {"names": fields.List(fields.String, example=["Alice", "Bob", "Clarice"])}
)

# General

ErrorMessageModel = api_models.model("Error Message", {"error": fields.String, "message": fields.String})

# Tags models

TagModel = api_models.model(
    "Tag",
    {
        "name": fields.String("Type_inference_error"),
        "color": fields.String("#dc3545"),
        "internal": fields.Boolean,
        "description": fields.String("The type of some variable can not be inferred"),
        "used_by": fields.List(fields.String),
        "mutable": fields.Boolean,
        "uuid": fields.String("c43d9d83-6267-40f6-ae94-c046bfe04476"),
    },
)

TagRequestModel = api_models.model(
    "Tag Request",
    {
        "name": fields.String("Type_inference_error"),
        "color": fields.String("#dc3545"),
        "internal": fields.Boolean,
        "description": fields.String("The type of some variable can not be inferred"),
    },
)

TagListModel = fields.List(Nested(TagModel))

# Ultimate models
UltimateVersionModel = api_models.model("Ultimate Version", {"version": fields.String})

UltimateConfigurationModel = api_models.model(
    "Ultimate Configuration", {"toolchain": fields.String, "user_settings": fields.String}
)

UltimateConfigurationsModel = api_models.model(
    "Ultimate Configurations",
    {"config_name_0": Nested(UltimateConfigurationModel), "config_name_1": Nested(UltimateConfigurationModel)},
)

UltimateResultModel = api_models.model(
    "Ultimate Result",
    {
        "shortDesc": fields.String,
        "longDesc": fields.String,
        "startLNr": fields.Integer,
        "endLNr": fields.Integer,
        "startCol": fields.Integer,
        "endCol": fields.Integer,
        "logLvl": fields.String,
        "type": fields.String,
    },
)

UltimateJobModel = api_models.model(
    "Ultimate Job",
    {
        "status": fields.String,
        "requestId": fields.String,
        "result": fields.List(Nested(UltimateResultModel)),
        "request_time": fields.String,
        "last_update": fields.String,
        "selected_requirements": fields.Wildcard(fields.Integer, example={"REQ_01": 1, "REQ_02": 2, "REQ_03": 0}),
        "result_requirements": fields.Wildcard(fields.Integer, example={"REQ_01": 1, "REQ_02": 2}),
    },
)

UltimateJobsModel = api_models.model("Ultimate Jobs", {"data": fields.List(Nested(UltimateJobModel))})

UltimateJobRequestModel = api_models.model(
    "Ultimate Job Request",
    {
        "req_file": fields.String,
        "configuration": fields.String,
        "req_ids": fields.List(fields.String),
    },
)
