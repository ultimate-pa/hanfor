from flask import Flask, current_app as fl_current_app
from json_db_connector.json_db import JsonDatabase
import ai.ai_core


class HanforFlask(Flask):
    db: JsonDatabase
    ai: ai.ai_core.AiCore


current_app: HanforFlask = fl_current_app  # noqa
