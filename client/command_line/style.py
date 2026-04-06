from prompt_toolkit.styles import Style

CLI_STYLE = Style.from_dict(
    {
        "output-field": "bg:#1e1e1e #d4d4d4",
        "welcome-field": "bg:#1e1e1e #55aaff bold",
        "input-field": "bg:#252526 #9cdcfe",
        "separator": "#444444",
        "prompt": "#00ff88 bold",
        "log-field": "bg:#1a1a2e #a0a8c0",
        "log-header": "bg:#16213e #7ec8e3 bold",
    }
)