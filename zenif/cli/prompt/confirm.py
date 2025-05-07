from ...constants import Keys
from ...schema import BooleanF, Schema
from .base import BasePrompt


class ConfirmPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._default: bool | None = None

        # Check if the field is a BooleanF
        if schema and not isinstance(self.field, BooleanF):
            field_type = type(self.field).__name__
            error_message = (
                f"ConfirmPrompt requires a BooleanF field, but got {field_type}"
            )
            raise TypeError(error_message)

    def default(self, value: bool) -> "ConfirmPrompt":
        """Set the default value for the prompt."""
        self._default = value
        return self

    def ask(self) -> bool:
        """Prompt the user for input."""
        options = (
            ["y", "N"]
            if self._default is False
            else ["Y", "n"]
            if self._default is True
            else ["y", "n"]
        )
        while True:
            self._print_prompt(
                self.message,
                options=options,
                default_option=(
                    "Y"
                    if self._default is True
                    else "N"
                    if self._default is False
                    else None
                ),
            )
            key = self._get_key().lower()
            result = (
                key == "y"
                if key in ("y", "n")
                else (
                    self._default
                    if key == Keys.ENTER and self._default is not None
                    else None
                )
            )
            if result is not None:
                error = self.validate(result or "")
                if not error:
                    self._print_prompt(
                        self.message,
                        value="Yes" if result else "No",
                        options=options,
                        default_option=(
                            "Y"
                            if self._default is True
                            else "N"
                            if self._default is False
                            else None
                        ),
                    )
                    print()
                    return result
                else:
                    self._print_prompt(self.message, error=error)
