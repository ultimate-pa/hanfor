from flask import Flask, current_app as fl_current_app
from json_db_connector.json_db import JsonDatabase


class HanforFlask(Flask):
    db: JsonDatabase


current_app: HanforFlask = fl_current_app  # noqa
