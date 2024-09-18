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
        if current_app.config["FEATURE_TELEMETRY"]:
            emit("command", "send_user_id")
            self.connections[request.sid] = TelemetryConnection(request.sid)  # noqa sid exists for request
        else:
            emit("command", "no_telemetry")
            disconnect()

    def on_disconnect(self):
        # end last event if needed
        if self.connections[request.sid].last_message["event"] == "open":  # noqa sid exists for request
            # TODO add auto_close event
            print(f"auto_close")
        del self.connections[request.sid]  # noqa sid exists for request

    def on_user_id(self, data):
        self.connections[request.sid].user_id = data  # noqa sid exists for request

    def on_event(self, data):
        tmp = json.loads(data)
        print(f"new event: {data}")
        # TODO add event
        self.connections[request.sid].last_message = tmp  # noqa sid exists for request
        pass
