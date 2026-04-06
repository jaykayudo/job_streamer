import asyncio
import threading

from client.web.app import app
from client.web.ws_server import WS_PORT, start_ws_server
from conf.settings import SETTINGS

WEB_PORT = SETTINGS.WEB_PORT
WEB_HOST = SETTINGS.WEB_HOST

WS_HOST = SETTINGS.WS_HOST
WS_PORT = SETTINGS.WS_PORT

def _run_flask():
    """Run Flask in its own thread (blocking)."""
    app.run(
        host=WEB_HOST,
        port=WEB_PORT,
        debug=False,   # must be False when running in a thread
        use_reloader=False,
    )


def main():
    print(f"Starting Job Streamer Web Client")
    print(f"  Flask  → http://{WEB_HOST}:{WEB_PORT}")
    print(f"  WS     → ws://{WS_HOST}:{WS_PORT}")

    # Flask runs in a background thread (it's sync/blocking).
    flask_thread = threading.Thread(target=_run_flask, daemon=True)
    flask_thread.start()

    # WebSocket server owns the async event loop on the main thread.
    asyncio.run(start_ws_server())


if __name__ == "__main__":
    main()
