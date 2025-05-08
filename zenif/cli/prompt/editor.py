from shutil import get_terminal_size

from colorama import Fore, Style
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_for_filename

# from pygments import highlight
from pygments.util import ClassNotFound

from ...constants import Cursor, Keys
from ...schema import Schema, StringF
from .base import BasePrompt


class EditorPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._language: str = "txt"

        # Check if the field is a StringF
        if schema and not isinstance(self.field, StringF):
            field_type = type(self.field).__name__
            error_message = (
                f"EditorPrompt requires a StringF field, but got {field_type}"
            )
            raise TypeError(error_message)

    def language(self, language: str) -> "EditorPrompt":
        """Set the file language for the prompt."""
        self._language = language
        return self

    def _get_lexer(self, ext: str) -> Lexer | None:
        try:
            return get_lexer_for_filename(
                f"editor.{ext}"
            )  # Filename doesn't matter, just the extension
        except ClassNotFound:
            return None

    def _update_cursor(
        self, cx: int, cy: int, char: str, columns: int, buffer: list[str]
    ) -> tuple:
        if char == Keys.UP:
            wrap_condition = cx > columns
            if cy > 0 or wrap_condition:
                if wrap_condition:
                    cx -= columns
                else:
                    cy -= 1
                cx = min(cx, len(buffer[cy]))
            elif cy == 0:
                cx = 0
        elif char == Keys.DOWN:
            wrap_condition = cx < columns and len(buffer[cy]) > columns
            if cy < len(buffer) - 1 or wrap_condition:
                if wrap_condition:
                    cx += columns
                else:
                    cy += 1
                cx = min(cx, len(buffer[cy]))
            elif cy == len(buffer) - 1:
                cx = len(buffer[cy])
        elif char == Keys.LEFT:
            if cx > 0:
                cx -= 1
            elif cy > 0:
                cy -= 1
                cx = len(buffer[cy])
        elif char == Keys.RIGHT:
            if cx < len(buffer[cy]):
                cx += 1
            elif cy < len(buffer) - 1:
                cy += 1
                cx = 0
        return cx, cy

    def ask(self) -> str:
        """Prompt the user for input."""

        # Prompt and error on first line
        # Controls on second line
        # Editor on third line and extends downward
        # After editor, language and other metrics (words, lines, etc.)

        buffer: list[str] = [""]
        output: str = ""

        cx: int = 0
        cy: int = 0
        pcx: int = 0
        pcy: int = 0

        indent: int = 2

        # lexer = self._get_lexer(self._language)

        controls: str = "Enter for newline, Ctrl+D to confirm"

        while True:
            error: str | None = self.validate("\n".join(buffer) or "")

            columns: int = get_terminal_size().columns

            self._print_prompt(self.message, error=error)
            print(
                f"\n{Cursor.lclear()}{Fore.RESET}{Style.DIM}  {controls}{Style.RESET_ALL}",
                end="",
            )

            output = ""

            for line in buffer:
                output += f"\n{Cursor.lclear()}{' ' * indent}{Fore.YELLOW}{line}{Style.RESET_ALL}"

            print(output, end="")

            if len(buffer[-1]) > 0:
                print(Cursor.left(len(buffer[-1])), end="")
            if len(buffer) > 1:
                print(Cursor.up(len(buffer) - 1), end="")

            # Move to cursor position
            if cx > 0:
                print(Cursor.cright(0, cx, columns), end="")
            if cy > 0:
                print(Cursor.down(cy), end="")

            pcx, pcy = cx, cy

            char = self._get_key()
            if char in Keys.ARROWS:
                cx, cy = self._update_cursor(cx, cy, char, columns, buffer)
            elif char == Keys.BACKSPACE:
                if cx > 0:
                    buffer[cy] = buffer[cy][: cx - 1] + buffer[cy][cx:]
                    cx -= 1
                elif cy > 0:
                    prev_line = buffer.pop(cy)
                    cy -= 1
                    cx = len(buffer[cy])
                    buffer[cy] += prev_line
            elif char == Keys.ENTER:
                buffer[cy] = buffer[cy][:cx]
                buffer.insert(cy + 1, buffer[cy][cx:])
                cy += 1
                cx = 0
            elif char == Keys.CTRLD:
                if not error and buffer:
                    print(Cursor.left(pcx), end="")
                    print(Cursor.up(pcy + 2), end="")
                    self._print_prompt(
                        self.message,
                        buffer[0].strip() + (" …" if len(buffer) > 1 else ""),
                    )
                    return "\n".join(buffer)
            else:
                buffer[cy] = buffer[cy][:cx] + char + buffer[cy][cx:]
                cx += 1

            # Reset the cursor position to prepare for the next render
            print(Cursor.left(pcx), end="")
            print(Cursor.up(pcy + 2), end="")
