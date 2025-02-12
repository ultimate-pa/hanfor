from flask_socketio import Namespace
from flask import request
import logging


class AiDataNamespace(Namespace):
    def __init__(self, namespace="/ai_data"):
        super().__init__(namespace)
        self.clients = {}

    def on_connect(self):
        sid = request.sid
        self.clients[sid] = {"user_id": None}
        logging.info(f"Client {sid} connected to AI Data WebSocket")

    def on_disconnect(self):
        sid = request.sid
        if sid in self.clients:
            del self.clients[sid]
        logging.info(f"Client {sid} disconnected from AI Data WebSocket")


def send_ai_update(send_dict, socketio):
    socketio.start_background_task(_emit_ai_update, send_dict, socketio)


def _emit_ai_update(send_dict, socketio):
    try:
        socketio.emit("ai_update", send_dict, namespace="/ai_data")
    except Exception as e:
        logging.error(f"Error sending AI Update: {e}")
