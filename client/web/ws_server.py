"""
WebSocket server — bridges browser clients to the action layer.

Protocol (JSON messages):
  Browser → Server:
    {"type": "command", "group": "bio", "subcommand": "create"}
    {"type": "input",   "value": "some text"}

  Server → Browser:
    {"type": "output",  "message": "...", "message_type": "info|error|success|warning"}
    {"type": "prompt",  "message": "Enter the name:"}
    {"type": "done"}
    {"type": "error",   "message": "..."}
    {"type": "log",     "level": "INFO|ERROR|WARNING", "message": "..."}
"""

import asyncio
import json
import threading
import weakref

from websockets.asyncio.server import ServerConnection, serve

from conf.settings import SETTINGS
from client.base.interactor import BaseInteractor
from client.command_line.parser import COMMAND_MAP
from utils.logging import JobStreamerLogger
from utils.types import MessageTitle, MessageType


logger = JobStreamerLogger().get_logger()

WS_HOST = SETTINGS.WS_HOST
WS_PORT = SETTINGS.WS_PORT

# All active connections — used by the log sink to broadcast to every client.
_clients: weakref.WeakSet[ServerConnection] = weakref.WeakSet()
_server_loop: asyncio.AbstractEventLoop | None = None
_log_sink_id: int | None = None


def _broadcast_log(message):
    """Loguru sink: sends every log record to all connected browser clients."""
    if _server_loop is None or not _clients:
        return
    record = message.record
    level = record["level"].name
    text = record["message"]
    payload = json.dumps({"type": "log", "level": level, "message": text})

    async def _send_all():
        for client in list(_clients):
            try:
                await client.send(payload)
            except Exception:
                pass

    _server_loop.call_soon_threadsafe(
        lambda: asyncio.ensure_future(_send_all(), loop=_server_loop)
    )


class WebInteractor(BaseInteractor):
    """Per-connection interactor. Sends output over WebSocket, blocks on reader()."""

    def __init__(self, ws: ServerConnection, loop: asyncio.AbstractEventLoop):
        self._ws = ws
        self._loop = loop
        self.is_busy = False

        self._reader_event: threading.Event | None = None
        self._reader_result: str = ""
        self._reader_lock = threading.Lock()

    # ------------------------------------------------------------------
    # BaseInteractor interface
    # ------------------------------------------------------------------

    def writer(
        self,
        message_type: MessageType,
        message: str,
        title: MessageTitle | None = None,
        extra_context: dict | list | None = None,
    ):
        _ = title, extra_context
        payload = json.dumps(
            {"type": "output", "message": message, "message_type": message_type.value}
        )
        asyncio.run_coroutine_threadsafe(self._ws.send(payload), self._loop)

    def reader(
        self,
        prompt: str,
        multiline: bool = False,
        extra_context: dict | None = None,
    ) -> str:
        _ = multiline, extra_context
        # Tell the browser it needs to provide input.
        payload = json.dumps({"type": "prompt", "message": prompt})
        asyncio.run_coroutine_threadsafe(self._ws.send(payload), self._loop)

        # Block the action thread until browser sends {"type": "input", "value": "..."}.
        event = threading.Event()
        with self._reader_lock:
            self._reader_result = ""
            self._reader_event = event
        event.wait()
        return self._reader_result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def resolve_input(self, value: str):
        """Called from the async WS loop when the browser sends an input message."""
        with self._reader_lock:
            if self._reader_event is not None:
                self._reader_result = value
                self._reader_event.set()
                self._reader_event = None


# ------------------------------------------------------------------
# Command dispatch
# ------------------------------------------------------------------

async def _run_command(
    interactor: WebInteractor, group: str, subcommand: str
):
    loop = asyncio.get_running_loop()
    interactor.is_busy = True
    try:
        if group not in COMMAND_MAP:
            await interactor._ws.send(
                json.dumps({"type": "error", "message": f"Unknown command: '{group}'"})
            )
            return

        action_cls = COMMAND_MAP[group]
        valid_subactions = action_cls.get_actions()

        if valid_subactions and subcommand not in valid_subactions:
            await interactor._ws.send(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Unknown subcommand '{subcommand}' for '{group}'",
                    }
                )
            )
            return

        action = action_cls(interactor)
        await loop.run_in_executor(
            None, action.handle_action_command, subcommand
        )
        await interactor._ws.send(json.dumps({"type": "done"}))

    except Exception as e:
        logger.error(f"WS command error: {e}")
        try:
            await interactor._ws.send(
                json.dumps({"type": "error", "message": str(e)})
            )
        except Exception:
            pass
    finally:
        interactor.is_busy = False


# ------------------------------------------------------------------
# Connection handler
# ------------------------------------------------------------------

async def _handle(ws: ServerConnection):
    global _clients
    loop = asyncio.get_running_loop()
    interactor = WebInteractor(ws, loop)
    _clients.add(ws)
    logger.info(f"WS client connected: {ws.remote_address}")

    try:
        async for raw in ws:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
                continue

            msg_type = data.get("type")

            if msg_type == "command":
                if interactor.is_busy:
                    await ws.send(
                        json.dumps(
                            {"type": "error", "message": "A command is already running"}
                        )
                    )
                    continue
                asyncio.create_task(
                    _run_command(interactor, data.get("group", ""), data.get("subcommand", ""))
                )

            elif msg_type == "input":
                interactor.resolve_input(data.get("value", ""))

    except Exception as e:
        logger.error(f"WS connection error: {e}")
    finally:
        logger.info(f"WS client disconnected: {ws.remote_address}")


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

async def start_ws_server():
    global _server_loop, _log_sink_id
    _server_loop = asyncio.get_running_loop()

    js_logger = JobStreamerLogger()
    _log_sink_id = js_logger.add_sink(
        _broadcast_log,
        level="DEBUG",
        format="{time:HH:mm:ss} | {level:<7} | {name} - {message}",
        enqueue=False,
    )

    try:
        async with serve(_handle, WS_HOST, WS_PORT) as server:
            logger.info(f"WebSocket server listening on ws://{WS_HOST}:{WS_PORT}")
            await server.serve_forever()
    finally:
        if _log_sink_id is not None:
            js_logger.logger.remove(_log_sink_id)