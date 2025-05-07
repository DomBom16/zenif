import shutil

from ...constants import Keys
from ...schema import Schema, StringF
from .base import BasePrompt


class PasswordPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._peeper: bool = False

        # Check if the field is a StringF
        if schema and not isinstance(self.field, StringF):
            field_type = type(self.field).__name__
            error_message = (
                f"PasswordPrompt requires a StringF field, but got {field_type}"
            )
            raise TypeError(error_message)

    def peeper(self) -> "PasswordPrompt":
        """Enable password peeper mode. This will show the last character typed unless it is a space or the last keypress was a backspace."""
        self._peeper = True
        return self

    def ask(self) -> str:
        """Prompt the user for input."""
        value = ""
        last_char = ""

        mask_char = "●"

        while True:
            error = self.validate(value or "")
            masked_value = mask_char * len(value)

            if self._peeper and last_char and last_char != " ":
                masked_value = masked_value[:-1] + last_char

            marker = "…"
            width = (
                shutil.get_terminal_size().columns
                - len(self.message)
                - len(error or "")
                - (2 if error else 0)
                - 4
            )
            truncated_value = (
                marker + masked_value[-(width - len(marker)) :]
                if len(masked_value) > width
                else masked_value
            )
            self._print_prompt(self.message, truncated_value, error=error)
            char = self._get_key()
            if char == Keys.ENTER:  # Enter key
                if not error and value:
                    # On submit, show the password fully masked again
                    masked_value = mask_char * len(value)
                    truncated_value = (
                        marker + masked_value[-(width - len(marker)) :]
                        if len(masked_value) > width
                        else masked_value
                    )
                    self._print_prompt(self.message, truncated_value, error=None)
                    print()  # Move to next line after input
                    return value
            elif char == Keys.BACKSPACE:  # Backspace
                value = value[:-1]
                last_char = ""  # Clear the last typed character on backspace
            elif char not in Keys.ARROWS:  # Ignore arrow keys
                last_char = (
                    char if char.strip() else ""
                )  # Update last_char only if non-space
                value += char
