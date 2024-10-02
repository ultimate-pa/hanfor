from hanfor_flask import current_app
from flask import request
from flask_socketio import emit, disconnect
from flask_socketio.namespace import Namespace
from dataclasses import dataclass
import json


@dataclass
class TelemetryConnection:
    sid: str
    user_id: str = ""
    last_message: dict = None


class TelemetryWs(Namespace):

    def __init__(self, namespace=None):
        self.connections: dict[str, TelemetryConnection] = {}
        super().__init__(namespace)

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
            # TODO add auto_close event
            print(f"auto_close")
        del self.connections[sid]

    def on_user_id(self, data):
        sid = request.sid  # noqa sid exists for request
        if sid in self.connections:
            self.connections[sid].user_id = data

    def on_event(self, data):
        sid = request.sid  # noqa sid exists for request
        tmp = json.loads(data)
        print(f"new event: {data}")
        # TODO add event
        if sid in self.connections:
            self.connections[sid].last_message = tmp
