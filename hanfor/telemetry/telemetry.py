from flask import request
from flask_socketio import emit, disconnect
from flask_socketio.namespace import Namespace


class TelemetryWs(Namespace):
    def on_connect(self):
        print("connected: " + request.sid)

    def on_disconnect(self):
        print("disconnected: " + request.sid)

    def on_userid(self, data):
        print(data)
        disconnect()


class TelemetryWs2(Namespace):
    def on_connect(self):
        print("connected2: " + request.sid)

    def on_disconnect(self):
        print("disconnected2: " + request.sid)
