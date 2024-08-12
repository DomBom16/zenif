import sys
from colorama import init, Fore, Style
import signal
from zenif.schema import Schema, StringF
import shutil

init(autoreset=True)


class BasePrompt:
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        self.message = message
        self.schema = schema
        self.id = id
        if schema and not id:
            raise ValueError("You must have an ID in order to use a schema.")
        if schema and id:
            self.field = schema.fields.get(id)
            if not self.field:
                raise ValueError(f"Field '{id}' not found in the schema.")
        else:
            self.field = None

    def validate(self, value):
        try:
            if self.schema and self.id:
                is_valid, errors, _ = self.schema.validate({self.id: value})
                if not is_valid:
                    return errors.get(self.id, ["Invalid input"])[0].rstrip(".")
            elif self.field:
                self.field.validate(value)
            return None
        except ValueError as e:
            return str(e)

    @staticmethod
    def _get_key():
        def handle_interrupt(signum, frame):
            raise KeyboardInterrupt()

        if sys.platform.startswith("win"):
            import msvcrt

            # Set up the interrupt handler
            signal.signal(signal.SIGINT, handle_interrupt)

            try:
                while True:
                    if msvcrt.kbhit():
                        char = msvcrt.getch().decode("utf-8")
                        if char == "\x03":  # Ctrl+C
                            raise KeyboardInterrupt()
                        return char
            finally:
                # Reset the interrupt handler
                signal.signal(signal.SIGINT, signal.SIG_DFL)

        else:
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                # Set up the interrupt handler
                signal.signal(signal.SIGINT, handle_interrupt)

                while True:
                    char = sys.stdin.read(1)
                    if char == "\x03":  # Ctrl+C
                        raise KeyboardInterrupt()
                    if char == "\x1b":
                        # Handle escape sequences (e.g., arrow keys)
                        next_char = sys.stdin.read(1)
                        if next_char == "[":
                            last_char = sys.stdin.read(1)
                            return f"\x1b[{last_char}"
                    return char
            finally:
                # Reset terminal settings and interrupt handler
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                signal.signal(signal.SIGINT, signal.SIG_DFL)

    @staticmethod
    def _print_prompt(
        prompt: str = "",
        value: str = "",
        default: any = None,
        options: list[str] | None = None,
        default_option: str | None = None,
        error: str | None = None,
    ):
        sys.stdout.write(f"\033[2K\r{Fore.GREEN}? {Fore.CYAN}{prompt}{Fore.RESET}")
        if default and not options:
            sys.stdout.write(f" {Fore.CYAN}{Style.DIM}({default}){Style.RESET_ALL}")
        if options:
            if default_option:
                options[
                    [option.lower() for option in options].index(default_option.lower())
                ] = options[
                    [option.lower() for option in options].index(default_option.lower())
                ].upper()
            if len(options) == 2:
                sys.stdout.write(
                    f" {Fore.CYAN}{Style.DIM}[{options[0]}/{options[1]}]{Style.RESET_ALL}"
                )
            else:
                sys.stdout.write(
                    f" {Fore.CYAN}{Style.DIM}[{"".join(options)}]{Style.RESET_ALL}"
                )
        sys.stdout.write(f"{Fore.CYAN}: {Fore.YELLOW}{value}")
        if error:
            sys.stdout.write(f"  {Fore.RED}{error}\033[{2 + len(error)}D")
        sys.stdout.flush()


class TextPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._default: str | None = None

    def default(self, value: str) -> "TextPrompt":
        self._default = value
        return self

    def ask(self) -> str:
        value = ""
        while True:
            error = self.validate(value or self._default or "")
            marker = "..."
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
            if char == "\r":  # Enter key
                if not error and (value or self._default):
                    self._print_prompt(
                        self.message, value or self._default, self._default
                    )
                    print()
                    return value or self._default
            elif char == "\x7f":  # Backspace
                value = value[:-1]
            elif char not in ("\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D"):
                value += char


class PasswordPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)

    def ask(self) -> str:
        value = ""
        while True:
            error = self.validate(value or "")
            masked_value = "*" * len(value)
            marker = "..."
            width = (
                shutil.get_terminal_size().columns
                - len(self.message)
                - len(error or "")
                - 2
                if error
                else 0 - 4
            )
            truncated_value = (
                marker + masked_value[-(width - len(marker)) :]
                if len(masked_value) > width
                else masked_value
            )
            self._print_prompt(self.message, truncated_value, error=error)
            char = self._get_key()
            if char == "\r":  # Enter key
                if not error and value:
                    print()  # Move to next line after input
                    return value
            elif char == "\x7f":  # Backspace
                value = value[:-1]
            elif char not in ("\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D"):
                value += char


class ConfirmPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._default: bool | None = None

    def default(self, value: bool) -> "ConfirmPrompt":
        self._default = value
        return self

    def ask(self) -> bool:
        options = (
            ["y", "N"]
            if self._default is False
            else ["Y", "n"] if self._default is True else ["y", "n"]
        )
        while True:
            self._print_prompt(
                self.message,
                options=options,
                default_option=(
                    "Y"
                    if self._default is True
                    else "N" if self._default is False else None
                ),
            )
            key = self._get_key().lower()
            result = (
                key == "y"
                if key in ("y", "n")
                else (
                    self._default if key == "\r" and self._default is not None else None
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
                            else "N" if self._default is False else None
                        ),
                    )
                    print()
                    return result
                else:
                    self._print_prompt(self.message, error=error)


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
        if not isinstance(self.field, StringF):
            field_type = type(self.field).__name__
            error_message = (
                f"ChoicePrompt requires a StringF field, but got {field_type}"
            )
            raise TypeError(error_message)

    def ask(self) -> str:
        current = 0
        print(
            f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n{Style.DIM}  Use Up/Down to navigate and Enter to select"
        )
        while True:
            for i, choice in enumerate(self.choices):
                if i == current:
                    print(f"{Fore.YELLOW}{Style.NORMAL}> {choice}{Fore.RESET}")
                else:
                    print(f"{Fore.YELLOW}{Style.DIM}  {choice}{Fore.RESET}")

            key = self._get_key()
            if key == "\r":  # Enter key
                result = self.choices[current]
                error = self.validate(result or "")
                if not error:
                    for _ in range(len(self.choices) + 2):
                        print(f"\033[1A\033[2K", end="")
                    self._print_prompt(self.message, result)
                    print()  # Move to next line
                    return result
                else:
                    for _ in range(len(self.choices) + 2):
                        print(f"\033[1A\033[2K", end="")
                    self._print_prompt(self.message, error=error)
                    print()
                    print(
                        f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n{Style.DIM}  Use Up/Down to navigate and Enter to select"
                    )
            elif key == "\x1b[A" and current > 0:  # Up arrow
                current -= 1
            elif key == "\x1b[B" and current < len(self.choices) - 1:  # Down arrow
                current += 1

            print(f"\033[{len(self.choices) + 1}A")  # Move cursor up to redraw choices


class CheckboxPrompt(BasePrompt):

    # TODO: Only show output on Enter like everything else

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
        selected = [False] * len(self.choices)
        current = 0
        print(
            f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n{Style.DIM}  Use Up/Down to navigate, Space to select, and Enter to confirm"
        )
        i = True
        while True:
            for i, (choice, is_selected) in enumerate(zip(self.choices, selected)):
                if i == current:
                    print(f"{Fore.YELLOW}{Style.DIM}X{Style.NORMAL}", end="")
                else:
                    print(f"{Fore.YELLOW} ", end="")
                print(
                    f"\r{f"{Fore.YELLOW}{"\033[4m" if i == current else ""}X\033[0m" if is_selected else '\033[1C'} {Fore.YELLOW}{Style.DIM}{choice}{Fore.RESET}"
                )

            if i:
                i = False
                result = [
                    choice
                    for choice, is_selected in zip(self.choices, selected)
                    if is_selected
                ]
                error = self.validate(result)

                print(f"\033[{len(self.choices) + 2}A", end="")
                self._print_prompt(self.message, error=f"{error if error else ""}\n")
                print(
                    f"\r{Fore.RESET}{Style.DIM}  Use Up/Down to navigate, Space to select, and Enter to confirm\033[{len(self.choices)}B"
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

            print(f"\033[{len(self.choices) + 2}A", end="")
            self._print_prompt(self.message, error=f"{error if error else ""}\n")
            print(
                f"\r{Fore.RESET}{Style.DIM}  Use Up/Down to navigate, Space to select, and Enter to confirm\033[{len(self.choices)}B"
            )

            if key == "\r" and not error:
                return result
            elif key == "\x1b[A" and current > 0:  # Up arrow
                current -= 1
            elif key == "\x1b[B" and current < len(self.choices) - 1:  # Down arrow
                current += 1

            print(f"\033[{len(self.choices) + 1}A")  # Move cursor up to redraw choices


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

    def default(self, value: int) -> "NumberPrompt":
        self._default = value
        return self

    def commas(self) -> "NumberPrompt":
        self._commas = True
        return self

    def ask(self) -> int:
        value = ""
        while True:
            try:
                int_value = (
                    int(value) if value else self._default if self._default else 0
                )
                error = self.validate(int_value)
            except ValueError:
                error = "Please enter a valid number."

            marker = "..."
            width = (
                shutil.get_terminal_size().columns
                - len(self.message)
                - len(error or "")
                - len(str(self._default or ""))
                - (7 if self._default else 5)
                - (2 if error else 0)
            )
            formatted_value = f"{int_value:,}" if self._commas and value else str(value)
            truncated_value = (
                marker + formatted_value[-(width - len(marker)) :]
                if len(formatted_value) > width
                else formatted_value
            )

            self._print_prompt(
                self.message, truncated_value, self._default, error=error
            )
            char = self._get_key()
            if char == "\r":  # Enter key
                if not error and (value or self._default is not None):
                    print()  # Move to next line after input
                    return float(value) if value else self._default
            elif char == "\x7f":  # Backspace
                value = value[:-1]
            elif char.isdigit() or char in ("-"):
                value += char


class Prompt:
    @staticmethod
    def text(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> TextPrompt:
        return TextPrompt(message, schema, id)

    @staticmethod
    def password(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> PasswordPrompt:
        return PasswordPrompt(message, schema, id)

    @staticmethod
    def confirm(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> ConfirmPrompt:
        return ConfirmPrompt(message, schema, id)

    @staticmethod
    def choice(
        message: str,
        choices: list[str],
        schema: Schema | None = None,
        id: str | None = None,
    ) -> ChoicePrompt:
        return ChoicePrompt(message, choices, schema, id)

    @staticmethod
    def checkbox(
        message: str,
        choices: list[str],
        schema: Schema | None = None,
        id: str | None = None,
    ) -> CheckboxPrompt:
        return CheckboxPrompt(message, choices, schema, id)

    @staticmethod
    def number(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> NumberPrompt:
        return NumberPrompt(message, schema, id)
