from prompt_toolkit.styles import Style

CLI_STYLE = Style.from_dict(
    {
        "output-field": "bg:#1e1e1e #d4d4d4",
        "input-field": "bg:#252526 #9cdcfe",
        "separator": "#444444",
        "prompt": "#00ff88 bold",
    }
)