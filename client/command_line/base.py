import asyncio
import threading
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.widgets import TextArea

from client.base.interactor import BaseInteractor
from utils.logging import JobStreamerLogger
from utils.types import MessageType, MessageTitle
from .style import CLI_STYLE
from .parser import COMMAND_MAP, parse_input, get_completions

WELCOME_MESSAGE = """\
     _       _       ____  _
    | | ___ | |__   / ___|| |_ _ __ ___  __ _ _ __ ___   ___ _ __
 _  | |/ _ \\| '_ \\  \\___ \\| __| '__/ _ \\/ _` | '_ ` _ \\ / _ \\ '__|
| |_| | (_) | |_) |  ___) | |_| | |  __/ (_| | | | | | |  __/ |
 \\___/ \\___/|_.__/  |____/ \\__|_|  \\___|\\__,_|_| |_| |_|\\___|_|

Type 'help' to see available commands. Press Ctrl+C to exit. Press Ctrl+T to toggle logs.
"""


LOG_PANE_MIN_WIDTH = 10
LOG_PANE_MAX_WIDTH = 50
LOG_PANE_DEFAULT_WIDTH = 50


class JobStreamerCLI(BaseInteractor):
    def __init__(self):
        # Threading bridge: when an action calls reader(), it sets this event
        # and blocks until _accept_input() resolves it with the next user input.
        self._reader_event: threading.Event | None = None
        self._reader_result: str = ""
        self._reader_lock = threading.Lock()

        self._log_visible: bool = False
        self._log_pane_width: int = LOG_PANE_DEFAULT_WIDTH
        self._log_sink_id: int | None = None
        # Condition instance bound to this object so keybindings can use it as a filter.
        self._tab_open = Condition(lambda: self._log_visible)

        self._setup()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup(self):
        welcome_lines = WELCOME_MESSAGE.count("\n") + 1
        self.welcome_window = Window(
            content=FormattedTextControl(WELCOME_MESSAGE),
            height=welcome_lines,
            style="class:welcome-field",
        )

        self.output_field = TextArea(
            text="",
            read_only=True,
            scrollbar=True,
            focusable=True,
            style="class:output-field",
            wrap_lines=True,
        )
        self.output_field.window.height = D(weight=3)

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
        self.input_field.window.height = D.exact(3)

        self.log_field = TextArea(
            text="── Logs ──\n",
            read_only=True,
            scrollbar=True,
            focusable=False,
            style="class:log-field",
            wrap_lines=True,
        )

        log_pane = ConditionalContainer(
            content=VSplit(
                [
                    Window(width=1, char="│", style="class:separator"),
                    HSplit(
                        [
                            Window(
                                content=FormattedTextControl(
                                    " Logs  Ctrl+k shrink  Ctrl+l grow  Ctrl+T close"
                                ),
                                height=1,
                                style="class:log-header",
                            ),
                            self.log_field,
                        ],
                        width=lambda: self._log_pane_width,
                    ),
                ]
            ),
            filter=Condition(lambda: self._log_visible),
        )

        main_pane = HSplit(
            [
                self.welcome_window,
                Window(height=1, char="─", style="class:separator"),
                self.output_field,
                Window(height=1, char="─", style="class:separator"),
                self.input_field,
            ]
        )

        layout = Layout(
            VSplit([main_pane, log_pane]),
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

        @kb.add("c-t")
        def _toggle_log(event):
            self._log_visible = not self._log_visible

        @kb.add("tab")
        def _cycle_focus(event):
            layout = event.app.layout
            if layout.has_focus(self.input_field):
                layout.focus(self.output_field)
            else:
                layout.focus(self.input_field)

        @kb.add("c-l", filter=self._tab_open)
        def _widen_log(event):
            self._log_pane_width = min(
                self._log_pane_width + 5, LOG_PANE_MAX_WIDTH
            )

        @kb.add("c-k", filter=self._tab_open)
        def _shrink_log(event):
            self._log_pane_width = max(
                self._log_pane_width - 5, LOG_PANE_MIN_WIDTH
            )

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
    
    def log(self, message: str):
        """Append a line to the log pane, safe to call from any thread."""
        def _write():
            current = self.log_field.text
            new_text = f"{current}\n{message}" if current else message
            self.log_field.buffer.set_document(
                Document(new_text, cursor_position=len(new_text)),
                bypass_readonly=True,
            )
            self.app.invalidate()

        try:
            loop = self.app.loop or asyncio.get_event_loop()
            loop.call_soon_threadsafe(_write)
        except RuntimeError:
            # No running event loop yet — write directly (startup messages).
            _write()
    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    async def run(self):
        js_logger = JobStreamerLogger()
        # Replace stdout sink with the TUI log pane.
        js_logger.remove_stdout_sink()
        self._log_sink_id = js_logger.add_sink(
            self._log_sink,
            level="INFO",
            format="{time:HH:mm:ss} | {level:<7} | {message}",
            backtrace=False,
            diagnose=False,
            enqueue=False,
        )
        try:
            await self.app.run_async()
        finally:
            if self._log_sink_id is not None:
                js_logger.logger.remove(self._log_sink_id)
                self._log_sink_id = None

    def _log_sink(self, message):
        """Loguru sink that writes to the TUI log pane."""
        self.log(str(message).rstrip())
