from colorama import Fore, Style

from ...constants import Cursor, Keys
from ...schema import Schema, StringF
from .base import BasePrompt


class ChoicePrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._choices = []

        # Check if the field is a StringF
        if schema and not isinstance(self.field, StringF):
            field_type = type(self.field).__name__
            error_message = (
                f"ChoicePrompt requires a StringF field, but got {field_type}"
            )
            raise TypeError(error_message)

    def choices(self, *choices: str | list[str]) -> "ChoicePrompt":
        """Set the choices for the prompt."""
        flattened = []
        for choice in choices:
            if isinstance(choice, list):
                flattened.extend(str(item) for item in choice)
            else:
                flattened.append(str(choice))
        self._choices = flattened
        return self

    def ask(self) -> str:
        """Prompt the user for input."""
        current = 0

        controls = "↑/↓ to navigate, Enter to confirm"

        check = "→"

        print(
            f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n{Style.DIM}  {controls}"
        )
        while True:
            for i, choice in enumerate(self._choices):
                if i > 0:
                    print()
                if i == current:
                    print(
                        f"{Fore.YELLOW}{Style.NORMAL}{check} {choice}{Fore.RESET}",
                        end="",
                    )
                else:
                    print(f"{Fore.YELLOW}{Style.DIM}  {choice}{Fore.RESET}", end="")

            key = self._get_key()
            if key == Keys.ENTER:  # Enter key
                result = self._choices[current]
                error = self.validate(result or "")
                if not error:
                    for _ in range(len(self._choices) + 1):
                        print(Cursor.lclear() + Cursor.up(1) + Cursor.lclear(), end="")
                    self._print_prompt(self.message, result)
                    print()  # Move to next line
                    return result
                else:
                    for _ in range(len(self._choices) + 1):
                        print(Cursor.lclear() + Cursor.up(1) + Cursor.lclear(), end="")
                    self._print_prompt(self.message, error=error)
                    print()
                    print(
                        f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n{Style.DIM}  {controls}"
                    )
            elif key == Keys.UP and current > 0:  # Up arrow
                current -= 1
            elif key == Keys.DOWN and current < len(self._choices) - 1:  # Down arrow
                current += 1

            print(Cursor.up(len(self._choices)))  # Move cursor up to redraw choices
