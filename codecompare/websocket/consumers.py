"""Django Channels WebSocket consumer for live code comparison."""
from __future__ import annotations
import asyncio, json, logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from channels.generic.websocket import AsyncWebsocketConsumer
    _CHANNELS_AVAILABLE = True
except ImportError:
    _CHANNELS_AVAILABLE = False
    class AsyncWebsocketConsumer:
        pass


if _CHANNELS_AVAILABLE:
    class ComparisonConsumer(AsyncWebsocketConsumer):
        async def connect(self) -> None:
            self.room_name = self.scope["url_route"]["kwargs"].get("room_name", "default")
            self.room_group_name = f"comparison_{self.room_name}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self._send_json({"type": "connected", "message": "Ready to compare"})

        async def disconnect(self, close_code: int) -> None:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
            if not text_data:
                return
            try:
                payload = json.loads(text_data)
            except json.JSONDecodeError:
                await self._send_json({"type": "error", "message": "Invalid JSON"})
                return
            msg_type = payload.get("type")
            if msg_type == "compare":
                await self._handle_compare(payload)
            elif msg_type == "ping":
                await self._send_json({"type": "pong"})

        async def _handle_compare(self, payload: dict[str, Any]) -> None:
            old_code = payload.get("old_code", "")
            new_code = payload.get("new_code", "")
            language = payload.get("language")
            if not old_code or not new_code:
                await self._send_json({"type": "error", "message": "old_code and new_code required"})
                return

            for stage, percent in [("parsing", 20), ("diff", 45), ("similarity", 65), ("ast", 80), ("plagiarism", 90), ("done", 95)]:
                await self._send_json({"type": "progress", "stage": stage, "percent": percent})
                await asyncio.sleep(0)

            try:
                import dataclasses
                from codecompare.core.services import ComparisonService
                result = await asyncio.get_event_loop().run_in_executor(
                    None, ComparisonService().compare, old_code, new_code, language)
                from codecompare.api.views import _result_to_dict
                await self._send_json({"type": "result", "data": _result_to_dict(result)})
            except Exception as exc:
                await self._send_json({"type": "error", "message": str(exc)})

        async def _send_json(self, data: dict) -> None:
            await self.send(text_data=json.dumps(data))

else:
    class ComparisonConsumer:
        pass
