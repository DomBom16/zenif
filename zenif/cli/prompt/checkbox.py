from colorama import Fore, Style

from ...constants import Cursor, Keys
from ...schema import ListF, Schema
from .base import BasePrompt


class CheckboxPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._choices = []

        # Check if the field is a ListF
        if schema and not isinstance(self.field, ListF):
            field_type = type(self.field).__name__
            error_message = (
                f"CheckboxPrompt requires a ListF field, but got {field_type}"
            )
            raise TypeError(error_message)

    def choices(self, *choices: str | list[str]) -> "CheckboxPrompt":
        """Set the choices for the prompt."""
        flattened = []
        for choice in choices:
            if isinstance(choice, list):
                flattened.extend(str(item) for item in choice)
            else:
                flattened.append(str(choice))
        self._choices = flattened
        return self

    def ask(self) -> list[str]:
        """Prompt the user for input."""
        selected = [False] * len(self._choices)
        current = 0

        controls = "↑/↓ to navigate, Space to select, Enter to confirm"

        check = "•"  # "X"
        hover = "○"  # check
        hovercheck = "●"  # f"\x1b[4m{check}\x1b[0m"

        print()
        print()

        i = True
        while True:
            for j, (choice, is_selected) in enumerate(zip(self._choices, selected)):
                print()
                if j == current:
                    print(f"{Fore.YELLOW}{Style.DIM}{hover}{Style.NORMAL}", end="")
                else:
                    print(f"{Fore.YELLOW} ", end="")
                print(
                    f"\r{f'{Fore.YELLOW}{hovercheck if j == current else check}{Style.RESET_ALL}' if is_selected else Cursor.right(1)} {Fore.YELLOW}{Style.DIM}{choice}{Fore.RESET}",
                    end="",
                )

            key = ""
            if i:
                i = False
                result = [
                    choice
                    for choice, is_selected in zip(self._choices, selected)
                    if is_selected
                ]
                error = self.validate(result)

                print(Cursor.up(len(self._choices) + 1), end="")
                self._print_prompt(self.message, error=f"{error if error else ''}\n")
                print(
                    f"\r{Fore.RESET}{Style.DIM}  {controls}{Cursor.down(len(self._choices) - 1)}"
                )
            else:
                key = self._get_key()
            if key == " ":
                selected[current] = not selected[current]

            result = [
                choice
                for choice, is_selected in zip(self._choices, selected)
                if is_selected
            ]
            error = self.validate(result)

            print(Cursor.up(len(self._choices) + 1), end="")
            self._print_prompt(self.message, error=f"{error if error else ''}\n")
            print(
                f"\r{Fore.RESET}{Style.DIM}  {controls}{Cursor.down(len(self._choices) - 1)}"
            )

            if key == Keys.ENTER and not error:
                for _ in range(len(self._choices) + 1):
                    print(Cursor.lclear() + Cursor.up(1) + Cursor.lclear(), end="")
                self._print_prompt(
                    self.message,
                    (
                        ", ".join(map(str, result[:-1])) + f", and {result[-1]}"
                        if len(result) > 1
                        else str(result[0])
                    ),
                )
                print()
                return result
            elif key == Keys.UP and current > 0:
                current -= 1
            elif key == Keys.DOWN and current < len(self._choices) - 1:
                current += 1

            print(Cursor.up(len(self._choices) + 1))  # Move cursor up to redraw choices
