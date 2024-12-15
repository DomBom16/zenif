from ..base import BasePrompt
from zenif.schema import Schema, StringF
from ....constants import Keys
from colorama import init, Fore, Style

init(autoreset=True)

class ChoicePrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        choices: list[str],
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self.choices = choices

        # Check if the field is a StringF
        if schema and not isinstance(self.field, StringF):
            field_type = type(self.field).__name__
            error_message = (
                f"ChoicePrompt requires a StringF field, but got {field_type}"
            )
            raise TypeError(error_message)

    def ask(self) -> str:
        """Prompt the user for input."""
        current = 0

        controls = "↑/↓ to navigate, Enter to confirm"

        print(
            f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n{Style.DIM}  {controls}"
        )
        while True:
            for i, choice in enumerate(self.choices):
                if i == current:
                    print(f"{Fore.YELLOW}{Style.NORMAL}> {choice}{Fore.RESET}")
                else:
                    print(f"{Fore.YELLOW}{Style.DIM}  {choice}{Fore.RESET}")

            key = self._get_key()
            if key == Keys.ENTER:  # Enter key
                result = self.choices[current]
                error = self.validate(result or "")
                if not error:
                    for _ in range(len(self.choices) + 2):
                        print(f"\x1b[1A\x1b[2K", end="")
                    self._print_prompt(self.message, result)
                    print()  # Move to next line
                    return result
                else:
                    for _ in range(len(self.choices) + 2):
                        print(f"\x1b[1A\x1b[2K", end="")
                    self._print_prompt(self.message, error=error)
                    print()
                    print(
                        f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n{Style.DIM}  {controls}"
                    )
            elif key == Keys.UP and current > 0:  # Up arrow
                current -= 1
            elif key == Keys.DOWN and current < len(self.choices) - 1:  # Down arrow
                current += 1

            print(f"\x1b[{len(self.choices) + 1}A")  # Move cursor up to redraw choices
