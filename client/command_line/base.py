import asyncio
import threading
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.widgets import TextArea

from client.base.interactor import BaseInteractor
from utils.types import MessageType, MessageTitle
from .style import CLI_STYLE
from .parser import COMMAND_MAP, parse_input, get_completions

WELCOME_MESSAGE = """\
     _       _       ____  _
    | | ___ | |__   / ___|| |_ _ __ ___  __ _ _ __ ___   ___ _ __
 _  | |/ _ \\| '_ \\  \\___ \\| __| '__/ _ \\/ _` | '_ ` _ \\ / _ \\ '__|
| |_| | (_) | |_) |  ___) | |_| | |  __/ (_| | | | | | |  __/ |
 \\___/ \\___/|_.__/  |____/ \\__|_|  \\___|\\__,_|_| |_| |_|\\___|_|

Type 'help' to see available commands. Press Ctrl+C to exit.
"""


class JobStreamerCLI(BaseInteractor):
    def __init__(self):
        # Threading bridge: when an action calls reader(), it sets this event
        # and blocks until _accept_input() resolves it with the next user input.
        self._reader_event: threading.Event | None = None
        self._reader_result: str = ""
        self._reader_lock = threading.Lock()

        self._setup()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup(self):
        self.output_field = TextArea(
            text=WELCOME_MESSAGE,
            read_only=True,
            scrollbar=True,
            focusable=False,
            style="class:output-field",
            wrap_lines=True,
        )

        self.input_field = TextArea(
            prompt=">>> ",
            multiline=False,
            wrap_lines=False,
            style="class:input-field",
            accept_handler=self._accept_input,
            focusable=True,
            completer=WordCompleter(get_completions(), sentence=True),
            complete_while_typing=True,
        )

        layout = Layout(
            HSplit(
                [
                    self.output_field,
                    Window(height=1, char="─", style="class:separator"),
                    self.input_field,
                ]
            ),
            focused_element=self.input_field,
        )

        self.app = Application(
            layout=layout,
            key_bindings=self._build_keybindings(),
            style=CLI_STYLE,
            full_screen=True,
            mouse_support=False,
        )

    def _build_keybindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("c-c")
        def _exit(event):
            event.app.exit()

        return kb

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    def _accept_input(self, buff: Buffer) -> bool:
        text = buff.text.strip()
        if not text:
            return False

        # If an action is waiting for follow-up input, hand the text to it.
        with self._reader_lock:
            if self._reader_event is not None:
                self._reader_result = text
                self._reader_event.set()
                self._reader_event = None
                return False

        # Otherwise treat as a new top-level command.
        self.notify(f">>> {text}")
        asyncio.get_event_loop().call_soon_threadsafe(
            lambda: asyncio.ensure_future(self._dispatch(text))
        )
        return False

    async def _dispatch(self, text: str):
        parsed = parse_input(text)
        if parsed is None:
            return

        group, subcommand = parsed

        if group not in COMMAND_MAP:
            self.notify(f"Unknown command: '{group}'. Type 'help' for a list of commands.")
            return

        action_cls = COMMAND_MAP[group]
        valid_subactions = action_cls.get_actions()

        # Commands like 'help' have no subactions — call handle_action_command directly.
        if not valid_subactions:
            action = action_cls(self)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, action.handle_action_command, subcommand)
            return

        if not subcommand:
            self.notify(
                f"'{group}' requires a subcommand. Available: {', '.join(valid_subactions)}"
            )
            return

        if subcommand not in valid_subactions:
            self.notify(
                f"Unknown subcommand '{subcommand}' for '{group}'. "
                f"Available: {', '.join(valid_subactions)}"
            )
            return

        action = action_cls(self)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, action.handle_action_command, subcommand)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def notify(self, message: str, message_type: MessageType = MessageType.INFO):
        """Append a line to the output field."""
        current = self.output_field.text
        new_text = f"{current}\n{message}" if current else message
        self.output_field.buffer.set_document(
            Document(new_text, cursor_position=len(new_text)),
            bypass_readonly=True,
        )

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
        self.notify(message, message_type)

    def reader(
        self,
        prompt: str,
        multiline: bool = False,
        extra_context: dict | None = None,
    ) -> str:
        """
        Block the calling (action) thread until the user submits the next input.
        The TUI event loop stays fully responsive while this waits.
        """
        _ = multiline, extra_context
        event = threading.Event()
        with self._reader_lock:
            self._reader_result = ""
            self._reader_event = event
        # Show the prompt in the output pane so the user knows what to type.
        self.notify(f"  {prompt}:")
        event.wait()
        return self._reader_result

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    async def run(self):
        await self.app.run_async()
