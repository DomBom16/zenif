import shutil

from ...constants import Keys
from ...schema import Schema, StringF
from .base import BasePrompt


class TextPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._default: str | None = None

        # Check if the field is a StringF
        if schema and not isinstance(self.field, StringF):
            field_type = type(self.field).__name__
            error_message = f"TextPrompt requires a StringF field, but got {field_type}"
            raise TypeError(error_message)

    def default(self, value: str) -> "TextPrompt":
        """Set the default value for the prompt."""
        self._default = value
        return self

    def ask(self) -> str:
        """Prompt the user for input."""
        value = ""
        while True:
            error = self.validate(value or self._default or "")
            marker = "…"
            width = (
                shutil.get_terminal_size().columns
                - len(self.message)
                - len(error or "")
                - len(self._default or "")
                - (6 if self._default else 4)
                - (2 if error else 0)
            )
            truncated_value = (
                marker + value[-(width - len(marker)) :]
                if len(value) > width
                else value
            )

            self._print_prompt(
                self.message, truncated_value, self._default, error=error
            )
            char = self._get_key()
            if char == Keys.ENTER:  # Enter key
                if not error and (value or self._default):
                    self._print_prompt(
                        self.message, value or self._default, self._default
                    )
                    print()
                    return value or self._default
            elif char == Keys.BACKSPACE:  # Backspace
                value = value[:-1]
            elif char == Keys.ESCAPE:  # Escape
                value = ""
            elif char not in Keys.ARROWS:
                value += char
