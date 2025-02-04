from .base import BasePrompt
from ...schema import Schema
from ...constants import Keys, Cursor

from colorama import Fore, Style


class CheckboxPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        choices: list[str],
        schema: Schema | None = None,
        id: str | None = None,
    ):

        super().__init__(message, schema, id)
        self.choices = choices

    def ask(self) -> list[str]:
        """Prompt the user for input."""
        selected = [False] * len(self.choices)
        current = 0

        controls = "↑/↓ to navigate, Space to select, Enter to confirm"

        print()

        i = True
        while True:
            for i, (choice, is_selected) in enumerate(zip(self.choices, selected)):
                if i == current:
                    print(f"{Fore.YELLOW}{Style.DIM}X{Style.NORMAL}", end="")
                else:
                    print(f"{Fore.YELLOW} ", end="")
                print(
                    f"\r{f"{Fore.YELLOW}{"\x1b[4m" if i == current else ""}X\x1b[0m" if is_selected else Cursor.right(1)} {Fore.YELLOW}{Style.DIM}{choice}{Fore.RESET}"
                )

            if i:
                i = False
                result = [
                    choice
                    for choice, is_selected in zip(self.choices, selected)
                    if is_selected
                ]
                error = self.validate(result)

                print(Cursor.up(len(self.choices) + 2), end="")
                self._print_prompt(self.message, error=f"{error if error else ""}\n")
                print(
                    f"\r{Fore.RESET}{Style.DIM}  {controls}{Cursor.down(len(self.choices))}"
                )

            key = self._get_key()
            if key == " ":  # Space
                selected[current] = not selected[current]

            result = [
                choice
                for choice, is_selected in zip(self.choices, selected)
                if is_selected
            ]
            error = self.validate(result)

            print(Cursor.up(len(self.choices) + 2), end="")
            self._print_prompt(self.message, error=f"{error if error else ""}\n")
            print(
                f"\r{Fore.RESET}{Style.DIM}  {controls}{Cursor.down(len(self.choices))}"
            )

            if key == Keys.ENTER and not error:
                for _ in range(len(self.choices) + 2):
                    print(Cursor.up(1) + Cursor.lclear(), end="")
                self._print_prompt(
                    self.message,
                    (
                        ", ".join(map(str, result[:-1])) + f", and {result[-1]}"
                        if len(result) > 1
                        else str(result[0])
                    ),
                )
                print()  # Move to next line
                return result
            elif key == Keys.UP and current > 0:  # Up arrow
                current -= 1
            elif key == Keys.DOWN and current < len(self.choices) - 1:  # Down arrow
                current += 1

            print(Cursor.up(len(self.choices) + 1))  # Move cursor up to redraw choices
