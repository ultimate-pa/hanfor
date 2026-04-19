from flask_socketio import Namespace
from flask import request
import logging


class AiAddonData(Namespace):
    def __init__(self, namespace="/ai_addon_data"):
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


def send_ai_update(send_dict: dict, event: str, socketio, sid: str | None = None):
    """Queue an AI update to be emitted via SocketIO in a background task"""
    socketio.start_background_task(_emit_ai_update, event, send_dict, socketio, sid)


def _emit_ai_update(event: str, send_dict: dict, socketio, sid: str | None = None):
    """Emit an AI update event to all clients or a specific client"""
    try:
        if sid:
            socketio.emit(event, send_dict, namespace="/ai_addon_data", to=sid)
        else:
            socketio.emit(event, send_dict, namespace="/ai_addon_data")
    except Exception as e:
        logging.error(f"Error sending AI update (event={event}): {e}")
