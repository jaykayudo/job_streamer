from flask import Flask, render_template

from client.command_line.parser import COMMAND_MAP
from client.web.ws_server import WS_HOST, WS_PORT

app = Flask(__name__)


@app.route("/")
def index():
    # Build command map for the template: {group: [subcommand, ...]}
    commands = {
        group: cls.get_actions() for group, cls in COMMAND_MAP.items()
    }
    return render_template(
        "index.html",
        commands=commands,
        ws_url=f"ws://{WS_HOST}:{WS_PORT}",
    )
