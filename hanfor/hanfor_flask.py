import datetime

from flask import Flask, current_app as fl_current_app, make_response

from ai_request.ai_core_requests import AiRequest
from json_db_connector.json_db import JsonDatabase
from functools import wraps, update_wrapper
from thread_handling.threading_core import ThreadHandler


class HanforFlask(Flask):
    ai_request: AiRequest
    thread_handler: ThreadHandler
    db: JsonDatabase


current_app: HanforFlask = fl_current_app  # noqa


def nocache(view):
    """Decorator for a flask view. If applied this will prevent caching."""

    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Last-Modified"] = str(datetime.datetime.now())
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response

    return update_wrapper(no_cache, view)
