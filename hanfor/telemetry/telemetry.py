from hanfor_flask import current_app
from flask import request
from flask_socketio import emit, disconnect, join_room, leave_room
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
        self.pause_state: dict[str, bool] = {}
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
            emit("command", "send_user_info")
            self.connections[sid] = TelemetryConnection(sid)
        else:
            emit("command", "no_telemetry")
            disconnect()

    def on_disconnect(self, _reason):
        # end last event if needed
        sid = request.sid  # noqa sid exists for request
        if sid in self.connections:
            if self.connections[sid].last_message and self.connections[sid].last_message["event"] == "open":
                self.__add_datapoint(*self.connections[sid].get_db_entry(auto_close=True))
            self.__add_datapoint("system", sid, self.connections[sid].user_id, "window_closed")
            uid = self.connections[sid].user_id
            leave_room(uid)
            del self.connections[sid]
            for c in self.connections.values():
                if c.user_id == uid:
                    return
            self.pause_state[uid] = False

    def on_user_info(self, data):
        sid = request.sid  # noqa sid exists for request
        if sid in self.connections:
            uid = data["user_id"]
            self.connections[sid].user_id = uid
            join_room(uid)
            if uid in self.pause_state and self.pause_state[uid]:
                emit("pause", "begin")
            self.__add_datapoint("system", sid, self.connections[sid].user_id, f"{data['path']}_window_opened")

    def on_event(self, data):
        sid = request.sid  # noqa sid exists for request
        tmp = json.loads(data)
        if tmp["scope"] == "system":
            tmp["id"] = sid
        if sid in self.connections:
            self.connections[sid].last_message = tmp
            self.__add_datapoint(*self.connections[sid].get_db_entry())

    def on_pause(self, enabled):
        sid = request.sid  # noqa sid exists for request
        if sid in self.connections:
            uid = self.connections[sid].user_id
            self.pause_state[uid] = enabled
            if enabled:
                emit("pause", "begin", room=uid)
            else:
                emit("pause", "end", room=uid)
