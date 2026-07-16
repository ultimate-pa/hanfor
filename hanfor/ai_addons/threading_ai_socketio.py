import logging
from typing import Optional

from flask import request
from flask_socketio import Namespace, SocketIO


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


class SendGuiUpdate:
    def __init__(self, socketio: Optional[SocketIO] = None):
        self.socketio = socketio

    def send_ai_update(self, send_object: object, event: str, sid: str | None = None):
        """Queue an AI update to be emitted via SocketIO in a background task"""
        if self.socketio:
            self.socketio.start_background_task(self.__emit_ai_update, event, send_object, sid)

    def __emit_ai_update(self, event: str, send_object: object, sid: str | None = None):
        """Emit an AI update event to all clients or a specific client"""
        try:
            if sid:
                self.socketio.emit(event, send_object, namespace="/ai_addon_data", to=sid)
            else:
                self.socketio.emit(event, send_object, namespace="/ai_addon_data")
        except Exception as e:
            logging.error(f"Error sending AI update (event={event}): {e}")
