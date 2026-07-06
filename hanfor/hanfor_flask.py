import datetime
from flask import Flask, current_app as fl_current_app, make_response
from json_db_connector.json_db import JsonDatabase
from functools import wraps, update_wrapper

from thread_handling.threading_core import ThreadHandler
from ai_request.ai_core_requests import AiRequest
from ai_addons.ai_addon_handler import AiAddons

from flask_restx import Api as Api_


class HanforFlask(Flask):
    ai_request: AiRequest
    ai_addons: AiAddons
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


class Api(Api_):

    def add_namespace(self, ns, path=None):
        if ns not in self.namespaces:
            self.namespaces.append(ns)
            self.sort_namespace()
            if self not in ns.apis:
                ns.apis.append(self)
            if path is not None:
                self.ns_paths[ns] = path

        for r in ns.resources:
            urls = self.ns_urls(ns, r.urls)
            self.register_resource(ns, r.resource, *urls, **r.kwargs)

        for name, definition in ns.models.items():
            self.models[name] = definition
        if not self.blueprint and self.app is not None:
            self._configure_namespace_logger(self.app, ns)

    def sort_namespace(self):
        self.namespaces = sorted(self.namespaces, key=lambda ns: ns.name)
