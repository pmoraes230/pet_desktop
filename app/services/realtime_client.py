import json
import os
import threading
import time
import base64
import hmac
import hashlib
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

try:
    from websocket import WebSocketApp
except ImportError:
    WebSocketApp = None

load_dotenv()


class RealtimeClient:
    def __init__(self, on_message=None, on_status=None, user_id=None, role=None):
        self.http_url = os.getenv("REALTIME_URL", "http://localhost:3000").rstrip("/")
        self.ws_url = os.getenv("REALTIME_WS_URL", "ws://localhost:3000").rstrip("/")
        self.api_token = os.getenv("REALTIME_API_TOKEN", "")
        self.websocket_token = os.getenv("REALTIME_WEBSOCKET_TOKEN", "")
        self.jwt_secret = os.getenv("REALTIME_JWT_SECRET", "")
        self.user_id = user_id
        self.role = role
        self.on_message = on_message
        self.on_status = on_status
        self.socket = None
        self.thread = None
        self.channels = set()

    def connect(self, channels):
        if WebSocketApp is None:
            self._status("Instale websocket-client para ativar o tempo real.")
            return False

        self.channels = {channel for channel in channels if channel}
        if not self.channels:
            self._status("Nenhum canal de tempo real configurado.")
            return False

        url = self.ws_url
        token = self._build_jwt() if self.jwt_secret else self.websocket_token
        if token:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{urlencode({'token': token})}"

        self.socket = WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self.thread = threading.Thread(target=self.socket.run_forever, daemon=True)
        self.thread.start()
        return True

    def publish(self, channel, event, payload):
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        response = requests.post(
            f"{self.http_url}/api/publish",
            json={"channel": channel, "event": event, "payload": payload},
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        return response.json()

    def close(self):
        if self.socket:
            self.socket.close()

    def _on_open(self, socket):
        self._status("Tempo real conectado.")
        for channel in self.channels:
            socket.send(json.dumps({"type": "subscribe", "channel": channel}))

    def _on_message(self, _socket, raw_message):
        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError:
            self._status("Mensagem de tempo real invalida.")
            return

        if self.on_message:
            self.on_message(message)

    def _on_error(self, _socket, error):
        self._status(f"Erro no tempo real: {error}")

    def _on_close(self, _socket, _status_code, _message):
        self._status("Tempo real desconectado.")

    def _status(self, message):
        if self.on_status:
            self.on_status(message)

    def _build_jwt(self):
        if not self.user_id or not self.role:
            return ""

        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": str(self.user_id),
            "user_id": str(self.user_id),
            "role": self.role,
            "exp": int(time.time()) + 3600,
        }

        signing_input = ".".join([
            self._base64url_json(header),
            self._base64url_json(payload),
        ])
        signature = hmac.new(
            self.jwt_secret.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return f"{signing_input}.{self._base64url(signature)}"

    def _base64url_json(self, value):
        raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
        return self._base64url(raw)

    def _base64url(self, value):
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")
