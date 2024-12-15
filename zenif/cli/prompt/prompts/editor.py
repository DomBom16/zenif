from ..base import BasePrompt
from zenif.schema import Schema
from zenif.log import Logger
from ....constants import Keys
from colorama import init, Fore, Style

from ....utils import wrap, strip_ansi
from ....constants import Keys
from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_for_filename
from pygments.styles import get_style_by_name, STYLE_MAP
from pygments.formatters import Terminal256Formatter as tformatter

init(autoreset=True)

class EditorPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._language: str = "txt"

    def language(self, language: str) -> "EditorPrompt":
        """Set the file language for the prompt."""
        self._language = language
        return self

    def _get_lexer(self, ext: str) -> Lexer | None:
        try:
            return get_lexer_for_filename(f"dummy.{ext}")
        except ClassNotFound:
            return None

    def _insert_char(self, value: str, char: str, cidx: int) -> str:
        cidx += value.count("\n")
        return value[:cidx] + char + value[cidx:]

    def _remove_char(self, value: str, cidx: int) -> str:
        return value[: cidx - 1] + value[cidx:]

    def ask(self) -> str:
        """Prompt the user for input."""

        Logger({"log_line": {"format": "simple"}}).warning(
            "EditorPrompt is in a very experimental state. Use at your own risk. Issues can be reported at https://github.com/DomBom16/zenif/issues."
        )

        # Prompt and error on first line
        # Controls on second line
        # Editor on third line and extends downward
        # After editor, language and other metrics (words, lines, etc.)

        buffer = [""]
        cx, cy = 0, 0

        print("\n")

        while True:
            error = self.validate("\n".join(buffer) or "")

            for _ in range(len(buffer) + 1):
                print(f"\x1b[1A\x1b[2K", end="")

            self._print_prompt(self.message, error=error)
            print(
                f"\n{Fore.RESET}{Style.DIM}  {(cx, cy)}{Style.RESET_ALL}",
                end="",
            )

            for line in buffer:
                print(
                    f"\n\x1b[2K{' ' * 2}{Fore.YELLOW}{strip_ansi(line)}{Style.RESET_ALL}",
                    end="",
                )

            char = self._get_key()
            if char == Keys.UP:  # Move cursor up
                if cy > 0:
                    cy -= 1
                    cx = min(cx, len(buffer[cy]))
                elif cy == 0:
                    cx = 0
            elif char == Keys.DOWN:  # Move cursor down
                if cy < len(buffer) - 1:
                    cy += 1
                    cx = min(cx, len(buffer[cy]))
                elif cy == len(buffer) - 1:
                    cx = len(buffer[cy])
            elif char == Keys.LEFT:  # Move cursor left
                if cx > 0:
                    cx -= 1
                elif cy > 0:
                    cy -= 1
                    cx = len(buffer[cy])
            elif char == Keys.RIGHT:  # Move cursor right
                if cx < len(buffer[cy]):
                    cx += 1
                elif cy < len(buffer) - 1:
                    cy += 1
                    cx = 0
            elif char == Keys.BACKSPACE:  # Handle backspace
                if cx > 0:
                    buffer[cy] = buffer[cy][: cx - 1] + buffer[cy][cx:]
                    cx -= 1
                elif cy > 0:
                    prev_line = buffer.pop(cy)
                    cy -= 1
                    cx = len(buffer[cy])
                    buffer[cy] += prev_line
            elif char == Keys.ENTER:  # Handle Enter (newline)
                new_line = buffer[cy][cx:]
                buffer[cy] = buffer[cy][:cx]
                buffer.insert(cy + 1, new_line)
                cy += 1
                cx = 0
            elif char == Keys.CTRLD:
                break
            else:
                buffer[cy] = buffer[cy][:cx] + char + buffer[cy][cx:]
                cx += 1
