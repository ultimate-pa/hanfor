from flask_restx import fields, Namespace
from flask_restx.fields import Nested

api_models = Namespace("API Models", description="API Models Namespace")


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
