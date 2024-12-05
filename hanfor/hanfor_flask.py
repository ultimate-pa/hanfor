from flask import Flask, current_app as fl_current_app
from json_db_connector.json_db import JsonDatabase
from hanfor.ai.ai_core import AiCore


class HanforFlask(Flask):
    db: JsonDatabase
    ai = AiCore()


current_app: HanforFlask = fl_current_app  # noqa
