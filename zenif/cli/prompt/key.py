from .base import BasePrompt


class KeyPrompt(BasePrompt):
    def __init__(self, message):
        super().__init__(message, None, None)
        self._keys: list[str] = []  # A list of keys

    def keys(self, *keys):
        """Set the keys for the prompt."""
        keys = list(keys)
        self._keys = keys
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
