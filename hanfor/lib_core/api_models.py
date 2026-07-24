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

# Requirements models

RequirementModel = api_models.model(
    "Requirement",
    {
        "id": fields.String(example="SysRS FooXY_42"),
        "desc": fields.String(example="The system shall ..."),
        "type": fields.String(example="Functional"),
        "tags": fields.List(fields.String, example=["unseen"]),
        "tags_comments": fields.Wildcard(fields.String, example={"unseen": ""}),
        "formal": fields.List(fields.String, example=["Globally, it is never the case that ..."]),
        "scope": fields.String(example="None"),
        "pattern": fields.String(example="None"),
        "vars": fields.List(fields.String, example=["bar", "foo"]),
        "pos": fields.Integer(example=1),
        "status": fields.String(example="Todo"),
        "csv_data": fields.Wildcard(fields.String, example={"col": "val"}),
        "type_inference_errors": fields.Wildcard(fields.List(fields.String), example={"0": ["p", "q"]}),
        "revision_diff": fields.Wildcard(fields.Raw, example={}),
    },
)

RequirementListModel = api_models.model(
    "Requirement List",
    {
        "data": fields.List(fields.Nested(RequirementModel)),
    },
)

RequirementDetailModel = api_models.model(
    "Requirement Detail",
    {
        "id": fields.String(example="SysRS FooXY_42"),
        "desc": fields.String(example="The system shall ..."),
        "type": fields.String(example="Functional"),
        "tags": fields.List(fields.String, example=["unseen"]),
        "tags_comments": fields.Wildcard(fields.String, example={"unseen": ""}),
        "formal": fields.List(fields.String, example=["Globally, it is never the case that ..."]),
        "scope": fields.String(example="None"),
        "pattern": fields.String(example="None"),
        "vars": fields.List(fields.String, example=["bar", "foo"]),
        "pos": fields.Integer(example=1),
        "status": fields.String(example="Todo"),
        "csv_data": fields.Wildcard(fields.String, example={"col": "val"}),
        "type_inference_errors": fields.Wildcard(fields.List(fields.String), example={"0": ["p", "q"]}),
        "revision_diff": fields.Wildcard(fields.Raw, example={}),
        "available_vars": fields.List(fields.String, example=["bar", "foo"]),
        "additional_static_available_vars": fields.List(fields.String, example=["TRUE", "FALSE"]),
        "next_id": fields.String(example="SysRS FooXY_43"),
    },
)

FormalizationModel = api_models.model(
    "Formalization",
    {
        "id": fields.Integer(example=0),
        "formalization_type": fields.String(example="formalization"),
        "text": fields.String(example='Globally, it is never the case that "foo != bar" holds.'),
        "order": fields.Integer(example=0),
        "scope": fields.String(example="GLOBALLY"),
        "pattern": fields.String(example="Absence"),
        "expr": fields.Wildcard(fields.String, example={"P": "", "R": "foo != bar"}),
    },
)

ColumnDefModel = api_models.model(
    "Column Def",
    {
        "target": fields.Integer(example=8),
        "csv_name": fields.String(example="csv_data.column_name"),
        "table_header_name": fields.String(example="csv: column_name"),
    },
)

ColumnDefsModel = api_models.model(
    "Column Defs",
    {
        "col_defs": fields.List(fields.Nested(ColumnDefModel)),
    },
)

SuccessResponseModel = api_models.model(
    "Success Response",
    {
        "success": fields.Boolean(example=True),
        "errormsg": fields.String(example=""),
    },
)

AvailableGuessModel = api_models.model(
    "Available Guess",
    {
        "scope": fields.String(example="GLOBALLY"),
        "pattern": fields.String(example="Absence"),
        "mapping": fields.Wildcard(fields.String, example={"P": "", "R": "foo != bar"}),
        "string": fields.String(example='Globally, it is never the case that "foo != bar" holds.'),
    },
)

AvailableGuessesModel = api_models.model(
    "Available Guesses",
    {
        "success": fields.Boolean(example=True),
        "errormsg": fields.String(example=""),
        "available_guesses": fields.List(fields.Nested(AvailableGuessModel)),
    },
)

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
