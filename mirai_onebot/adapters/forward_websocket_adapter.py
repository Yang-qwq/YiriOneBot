import secrets
from typing import Optional, Union, Any, Dict
from websockets.legacy.client import WebSocketClientProtocol
from .base import Adapter
import json
import asyncio
import websockets
import logging

logger = logging.getLogger(__name__)


class ForwardWebsocketAdapter(Adapter):
    def __init__(
        self, uri: str, access_token: str, reconnect_interval: int = 1
    ) -> None:
        super().__init__(access_token)

        self.ws_uri = uri
        self.reconnect_interval = reconnect_interval
        self.ws_client: Optional[WebSocketClientProtocol] = None

        self._internal_event_bus.subscribe("onebot_message", self._message_parser)

    def start(self):
        asyncio.get_event_loop().create_task(self._event_receiver())

    async def _message_parser(self, message: str):
        try:
            data = json.loads(message)
        except json.JSONDecodeError as e:
            logger.error("无法解析 OneBot 实现的消息。")
            logger.exception(e)
            return

        if not isinstance(data, dict):
            logger.error("OneBot 实现的消息不是一个字典。")
            return

        if (
            data.get("detail_type", None) is not None
            and data.get("sub_type", None) is not None
        ):
            # 响应或其他
            await self._internal_event_bus.emit("onebot_resp", data)
        else:
            await self.emit("onebot_event", data)

    async def _event_receiver(self):
        while True:
            async with websockets.connect(
                self.ws_uri,
                extra_headers={"Authorization": f"Bearer {self.access_token}"},
            ) as ws:
                self.ws_client = ws

                while True:
                    try:
                        data = await ws.recv()

                        if isinstance(data, bytes):
                            data = data.decode("utf-8")

                        await self._internal_event_bus.emit("onebot_message", data)
                    except RuntimeError as e:
                        logger.error("接收 OneBot 实现的消息时错误。")
                        logger.exception(e)
                    except websockets.ConnectionClosed:
                        logger.info("OneBot 实现断开连接，尝试重连。")
                        break

            await asyncio.sleep(self.reconnect_interval)

    async def _call_api(
        self, action: str, params: dict, echo: Optional[str] = None
    ) -> Union[Dict[str, Any], None]:
        if echo is None:
            echo = secrets.token_hex(8)

        if self.ws_client is None or self.ws_client.closed:
            raise ConnectionResetError("OneBot 实现连接已断开")

        response: Optional[Union[Dict[str, Any], None]] = None
        received = asyncio.Event()

        @self._internal_event_bus.on("onebot_resp")
        async def response_handler(data: Dict[str, Any]):
            nonlocal response, received
            if data["echo"] == echo:
                response = data
                received.set()
                self._internal_event_bus.unsubscribe("onebot_resp", response_handler)

        await self.ws_client.send(
            json.dumps({"action": action, "params": params, "echo": echo})
        )

        await received.wait()

        return response
