import shutil

from colorama import Style

from ...constants import Keys
from ...schema import FloatF, IntegerF, Schema
from .base import BasePrompt


class NumberPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._default: int | None = None
        self._commas: bool = False
        self._allow_decimals: bool = False
        self._allow_negatives: bool = False

        # Check if the field is a IntegerF or FloatF
        if schema and not isinstance(self.field, (IntegerF, FloatF)):
            field_type = type(self.field).__name__
            error_message = f"NumberPrompt requires an IntegerF or FloatF field, but got {field_type}"
            raise TypeError(error_message)

    def default(self, value: int) -> "NumberPrompt":
        """Set the default value for the prompt."""
        self._default = value
        return self

    def commas(self) -> "NumberPrompt":
        """Use commas to separate thousands in the prompt. This does not affect the validation or the returned value."""
        self._commas = True
        return self

    def allow_decimals(self) -> "NumberPrompt":
        """Allow decimals in the prompt. If using a schema, you must use the FloatF type."""
        self._allow_decimals = True
        return self

    def allow_negatives(self) -> "NumberPrompt":
        """Allow negative numbers in the prompt."""
        self._allow_negatives = True
        return self

    def ask(self) -> int:
        """Prompt the user for input."""
        value = ""
        while True:
            try:
                if self._allow_decimals:
                    # Parse as float if decimals are allowed
                    float_value = (
                        float(value) if value else self._default if self._default else 0
                    )
                    int_value = (
                        int(float_value) if float_value.is_integer() else float_value
                    )
                else:
                    # Parse as integer
                    int_value = (
                        int(value) if value else self._default if self._default else 0
                    )
                error = self.validate(
                    float_value if self._allow_decimals else int_value
                )
            except ValueError:
                error = "Please enter a valid number."

            marker = "…"
            width = (
                shutil.get_terminal_size().columns
                - len(self.message)
                - len(error or "")
                - len(str(self._default or ""))
                - (7 if self._default else 5)
                - (2 if error else 0)
            )

            if value:
                if self._allow_decimals and self._commas:
                    raise ValueError("Cannot use both commas and decimals.")

                if self._allow_decimals:
                    # Format with at least 1 decimal place but full precision
                    formatted_value = (
                        f"{float_value:.0f}{Style.DIM}.{Style.NORMAL}"
                        if "." not in value
                        else value
                    )
                elif self._commas:
                    # Format with commas if applicable
                    formatted_value = f"{int_value:,}"
                else:
                    formatted_value = str(value)
            else:
                formatted_value = str(value)
            truncated_value = (
                marker + formatted_value[-(width - len(marker)) :]
                if len(formatted_value) > width
                else formatted_value
            )

            self._print_prompt(
                self.message, truncated_value, self._default, error=error
            )
            char = self._get_key()
            if char == Keys.ENTER:  # Enter key
                if not error and (value or self._default is not None):
                    print()  # Move to next line after input
                    return (
                        float(value)
                        if self._allow_decimals and value
                        else (int(value) if value else self._default)
                    )
            elif char == Keys.BACKSPACE:  # Backspace
                value = value[:-1]
            elif char.isdigit() and len(value) < 15:
                value += char
            elif char == "." and self._allow_decimals and "." not in value:
                value += "."
            elif char == "-" and self._allow_negatives:
                # toggle negative sign on/off
                if value and value[0] == "-":
                    value = value[1:]
                else:
                    value = "-" + value
            elif char == Keys.UP:  # Up arrow
                value = str(int(value or 0) + 1)
            elif char == Keys.DOWN:  # Down arrow
                value = str(int(value or 0) - 1)

            if value == "-":
                value = ""
