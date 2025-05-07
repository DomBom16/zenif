from ...schema import Schema, StringF
from .base import BasePrompt


class KeyPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._keys: list[str] = []  # A list of keys

        # Check if the field is a StringF
        if schema and not isinstance(self.field, StringF):
            field_type = type(self.field).__name__
            error_message = f"KeyPrompt requires a StringF field, but got {field_type}"
            raise TypeError(error_message)

    def keys(self, *keys: str):
        """Set the keys for the prompt."""
        self._keys = list(keys)
        return self

    def ask(self) -> str:
        """Prompt the user for input."""
        while True:
            self._print_prompt(self.message)
            key = self._get_key().lower()
            if key in self._keys:
                self._print_prompt(self.message, value=key)
                print()
                return key
