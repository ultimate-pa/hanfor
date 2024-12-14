from hanfor_flask import current_app
from flask import request
from flask_socketio import emit, disconnect
from flask_socketio.namespace import Namespace
from dataclasses import dataclass
from os import path
import json
from tinyflux import TinyFlux, Point
from datetime import datetime


@dataclass
class TelemetryConnection:
    sid: str
    user_id: str = ""
    last_message: dict = None

    def get_db_entry(self, auto_close: bool = False) -> tuple[str, str, str, str]:
        if self.last_message:
            if auto_close:
                return self.last_message["scope"], self.last_message["id"], self.user_id, "auto_close"
            else:
                return self.last_message["scope"], self.last_message["id"], self.user_id, self.last_message["event"]
        return "", "", "", ""


class TelemetryWs(Namespace):

    def __init__(self, namespace=None):
        self.connections: dict[str, TelemetryConnection] = {}
        self.db: TinyFlux | None = None
        super().__init__(namespace)

    def set_data_folder(self, data_folder: str):
        self.db = TinyFlux(path.join(data_folder, "telemetry_data.csv"))

    def __add_datapoint(self, scope: str, data_id: str, user_id: str, event: str):
        print(f"add data: {scope}, {data_id}, {user_id}, {event}")
        if self.db is not None:
            p = Point(time=datetime.now(), measurement=scope, tags={"id": data_id, "uid": user_id, "event": event})
            self.db.insert(p, compact_key_prefixes=True)

    def on_connect(self):
        sid = request.sid  # noqa sid exists for request
        if current_app.config["FEATURE_TELEMETRY"]:
            emit("command", "send_user_id")
            self.connections[sid] = TelemetryConnection(sid)
        else:
            emit("command", "no_telemetry")
            disconnect()

    def on_disconnect(self):
        # end last event if needed
        sid = request.sid  # noqa sid exists for request
        if (
            sid in self.connections
            and self.connections[sid].last_message
            and self.connections[sid].last_message["event"] == "open"
        ):
            self.__add_datapoint(*self.connections[sid].get_db_entry(auto_close=True))
        self.__add_datapoint("system", sid, self.connections[sid].user_id, "window_closed")
        del self.connections[sid]

    def on_user_id(self, data):
        sid = request.sid  # noqa sid exists for request
        if sid in self.connections:
            self.connections[sid].user_id = data
            self.__add_datapoint("system", sid, self.connections[sid].user_id, "window_opened")

    def on_event(self, data):
        sid = request.sid  # noqa sid exists for request
        tmp = json.loads(data)
        if sid in self.connections:
            self.connections[sid].last_message = tmp
            self.__add_datapoint(*self.connections[sid].get_db_entry())
