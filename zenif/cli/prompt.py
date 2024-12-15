import sys
from colorama import init, Fore, Style, Back
import signal
from zenif.schema import Schema, StringF
from zenif.log import Logger
import shutil
from datetime import datetime

# For the upcoming EditorPrompt
from ..utils import wrap, strip_ansi
from ..constants import Keys
from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_for_filename
from pygments.styles import get_style_by_name, STYLE_MAP
from pygments.formatters import Terminal256Formatter as tformatter

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
                        if char == Keys.CTRLC:  # Ctrl+C
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
                    if char == Keys.CTRLC:  # Ctrl+C
                        raise KeyboardInterrupt()
                    if char == Keys.ESCAPE:
                        # Handle escape sequences (e.g., arrow keys)
                        next_char = sys.stdin.read(1)
                        if next_char == "[":
                            last_char = sys.stdin.read(1)
                            return f"\033[{last_char}"
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
        """Set the default value for the prompt."""
        self._default = value
        return self

    def ask(self) -> str:
        """Prompt the user for input."""
        value = ""
        while True:
            error = self.validate(value or self._default or "")
            marker = "…"
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
            if char == Keys.ENTER:  # Enter key
                if not error and (value or self._default):
                    self._print_prompt(
                        self.message, value or self._default, self._default
                    )
                    print()
                    return value or self._default
            elif char == Keys.BACKSPACE:  # Backspace
                value = value[:-1]
            elif char == Keys.ESCAPE:  # Escape
                value = ""
            elif char not in Keys.ARROWS:
                value += char


class PasswordPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._peeper: bool = False

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
        """Set the default value for the prompt."""
        self._default = value
        return self

    def ask(self) -> bool:
        """Prompt the user for input."""
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
                        f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n{Style.DIM}  {controls}"
                    )
            elif key == Keys.UP and current > 0:  # Up arrow
                current -= 1
            elif key == Keys.DOWN and current < len(self.choices) - 1:  # Down arrow
                current += 1

            print(f"\033[{len(self.choices) + 1}A")  # Move cursor up to redraw choices


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
                print(f"\r{Fore.RESET}{Style.DIM}  {controls}\033[{len(self.choices)}B")

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
            print(f"\r{Fore.RESET}{Style.DIM}  {controls}\033[{len(self.choices)}B")

            if key == Keys.ENTER and not error:
                for _ in range(len(self.choices) + 2):
                    print(f"\033[1A\033[2K", end="")
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
        self._allow_decimals: bool = False
        self._allow_negatives: bool = False

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


class DatePrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._default: tuple[int, int, int] | None = None
        self._month_first: bool = False  # day-month or month-day

        self._year_range: tuple[int, int] = (1900, 2100)

        self._sep: str = "/"

        self._show_words: bool = False

        self.current_field_idx = 0

        self.day: str = ""
        self.month: str = ""
        self.year: str = ""

    def default(self, value: tuple[int, int, int]) -> "DatePrompt":
        """Set the default value for the prompt."""
        self._default = value
        self.day, self.month, self.year = map(str, self._default)
        return self

    def month_first(self) -> "DatePrompt":
        """Use month-day-year instead of day-month-year."""
        self._month_first = True
        return self

    def year_range(self, start: int, end: int) -> "DatePrompt":
        """Set the minimum and maximum years for the prompt. Any values that exceed the range will be capped."""
        self._year_range = (start, end)
        return self

    def separator(self, sep: str) -> "DatePrompt":
        """Set the separator between the day, month, and year fields."""
        self._sep = sep
        return self

    def show_words(self) -> "DatePrompt":
        """On submit, display the submitted date in words. Ex: 1/1/2014 -> January 1, 2014"""
        self._show_words = True
        return self

    def ask(self) -> datetime:
        """Prompt the user for input."""
        field_order = (
            ["month", "day", "year"] if self._month_first else ["day", "month", "year"]
        )

        print("\n\n")

        fresh = False

        while True:
            controls = "←/→ to navigate, Tab to highlight, Enter to confirm"

            error = self.validate(
                f"{self.month or 'MM'}/{self.day or 'DD'}/{self.year or 'YYYY'}"
            )

            for _ in range(3):
                print(f"\033[1A\033[2K", end="")
            self._print_prompt(self.message, error=error)
            print(f"\n{Fore.RESET}{Style.DIM}  {controls}")

            formatted_value = f"  {Fore.YELLOW}{Back.RESET}{"" if self.current_field_idx == 0 else Style.DIM}{f"{Fore.BLACK}{Back.YELLOW}" if self.current_field_idx == 0 and fresh else ''}"

            formatted_value += (
                (self.month or "MM").rjust(2, "0")
                if self._month_first
                else (self.day or "DD").rjust(2, "0")
            )

            formatted_value += f"{Fore.YELLOW}{Back.RESET}{Style.DIM}{self._sep}{Style.NORMAL if self.current_field_idx == 1 else ""}{f"{Fore.BLACK}{Back.YELLOW}" if self.current_field_idx == 1 and fresh else ''}"

            formatted_value += (
                (self.day or "DD").rjust(2, "0")
                if self._month_first
                else (self.month or "MM").rjust(2, "0")
            )

            formatted_value += f"{Fore.YELLOW}{Back.RESET}{Style.DIM}{self._sep}{Style.NORMAL if self.current_field_idx == 2 else ""}{f"{Fore.BLACK}{Back.YELLOW}" if self.current_field_idx == 2 and fresh else ''}"

            formatted_value += (self.year or "YYYY").rjust(4, "0")

            formatted_value += f"{Style.RESET_ALL}"

            print(f"{formatted_value}")

            char = self._get_key()
            if char == Keys.TAB or char == Keys.RIGHT:  # Tab
                # move to next field
                self.current_field_idx = (self.current_field_idx + 1) % 3
                if int(self.year or 0) < self._year_range[0] and self.year:
                    self.year = str(self._year_range[0])
                fresh = char == Keys.TAB
            elif char == Keys.STAB or char == Keys.LEFT:  # Shift+Tab or Left arrow
                # move to previous field
                self.current_field_idx = (self.current_field_idx - 1) % 3
                if int(self.year or 0) < self._year_range[0] and self.year:
                    self.year = str(self._year_range[0])
                fresh = char == Keys.STAB
            elif char == Keys.ENTER:  # Enter key
                # check if all fields are filled
                if (
                    1 <= int(self.day) <= 31
                    and 1 <= int(self.month) <= 12
                    and (self._year_range[0] <= int(self.year) <= self._year_range[1])
                ):
                    months = [
                        "January",
                        "February",
                        "March",
                        "April",
                        "May",
                        "June",
                        "July",
                        "August",
                        "September",
                        "October",
                        "November",
                        "December",
                    ]

                    for _ in range(3):
                        print(f"\033[1A\033[2K", end="")
                    self._print_prompt(
                        self.message,
                        (
                            f"{months[int(self.month or 0) - 1]} {self.day or ""}, {self.year or ""}"
                            if self._show_words
                            else f"{int(self.month if self._month_first else self.day)}{self._sep}{int(self.day if self._month_first else self.month)}{self._sep}{int(self.year)}"
                        ),
                    )
                    print()
                    return datetime(int(self.year), int(self.month), int(self.day))
            elif char == Keys.BACKSPACE:  # Backspace
                if field_order[self.current_field_idx] == "day":
                    self.day = self.day[:-1]
                    if self.day == "0" or fresh:
                        self.day = ""
                elif field_order[self.current_field_idx] == "month":
                    self.month = self.month[:-1]
                    if self.month == "0" or fresh:
                        self.month = ""
                elif field_order[self.current_field_idx] == "year":
                    self.year = self.year[:-1]
                    if self.year == "0" or fresh:
                        self.year = ""
                fresh = False
            elif char == Keys.UP:  # Up arrow
                if field_order[self.current_field_idx] == "day":
                    self.day = str((int(self.day or 0) + 1) % 32)
                elif field_order[self.current_field_idx] == "month":
                    self.month = str((int(self.month or 0) + 1) % 13)
                elif field_order[self.current_field_idx] == "year":
                    self.year = str(int(self.year or str(datetime.now().year)) + 1)
                    if int(self.year) > self._year_range[1]:
                        self.year = str(self._year_range[0])  # Wrap around
                fresh = False
            elif char == Keys.DOWN:  # Down arrow
                if field_order[self.current_field_idx] == "day":
                    self.day = str((int(self.day or 0) - 1) % 32)
                elif field_order[self.current_field_idx] == "month":
                    self.month = str((int(self.month or 0) - 1) % 13)
                elif field_order[self.current_field_idx] == "year":
                    self.year = str(int(self.year or str(datetime.now().year)) - 1)
                    if int(self.year) < self._year_range[0]:
                        self.year = str(self._year_range[1])  # Wrap around
                fresh = False
            elif char.isdigit():
                fprev = fresh
                fresh = False
                if field_order[self.current_field_idx] == "day":
                    if fprev:
                        self.day = ""
                    if len(self.day.lstrip("0")) < 2:
                        self.day = self.day.lstrip("0") + char
                    if int(self.day) > 31:
                        self.day = "31"
                    if len(self.day) == 2 or int(self.day) > 3:
                        self.current_field_idx = (self.current_field_idx + 1) % 3
                        fresh = True
                elif field_order[self.current_field_idx] == "month":
                    if fprev:
                        self.month = ""
                    if len(self.month.lstrip("0")) < 2:
                        self.month = self.month.lstrip("0") + char
                    if int(self.month) > 12:
                        self.month = "12"
                    if len(self.month) == 2 or int(self.month) > 1:
                        self.current_field_idx = (self.current_field_idx + 1) % 3
                        fresh = True
                elif field_order[self.current_field_idx] == "year":
                    if fprev:
                        self.year = ""
                    if len(self.year.lstrip("0")) < 4:
                        self.year = self.year.lstrip("0") + char
                    if int(self.year) > self._year_range[1]:
                        self.year = str(self._year_range[1])
                    if len(self.year) == 4:
                        self.current_field_idx = (self.current_field_idx + 1) % 3
                        fresh = True


class EditorPrompt(BasePrompt):
    def __init__(
        self,
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ):
        super().__init__(message, schema, id)
        self._language: str = "txt"

    def language(self, language: str) -> "EditorPrompt":
        """Set the file language for the prompt."""
        self._language = language
        return self

    def _get_lexer(self, ext: str) -> Lexer | None:
        try:
            return get_lexer_for_filename(f"dummy.{ext}")
        except ClassNotFound:
            return None

    def _insert_char(self, value: str, char: str, cidx: int) -> str:
        cidx += value.count("\n")
        return value[:cidx] + char + value[cidx:]

    def _remove_char(self, value: str, cidx: int) -> str:
        return value[: cidx - 1] + value[cidx:]

    def ask(self) -> str:
        """Prompt the user for input."""

        Logger({"log_line": {"format": "simple"}}).warning("EditorPrompt is in a very experimental state. Use at your own risk. Issues can be reported at https://github.com/DomBom16/zenif/issues.")

        # Prompt and error on first line
        # Controls on second line
        # Editor on third line and extends downward
        # After editor, language and other metrics (words, lines, etc.)

        buffer = [""]
        cx, cy = 0, 0

        print("\n")

        while True:
            error = self.validate("\n".join(buffer) or "")

            for _ in range(len(buffer) + 1):
                print(f"\033[1A\033[2K", end="")

            self._print_prompt(self.message, error=error)
            print(
                f"\n{Fore.RESET}{Style.DIM}  {(cx, cy)}{Style.RESET_ALL}",
                end="",
            )

            for line in buffer:
                print(
                    f"\n\033[2K{' ' * 2}{Fore.YELLOW}{strip_ansi(line)}{Style.RESET_ALL}",
                    end="",
                )

            char = self._get_key()
            if char == Keys.UP:  # Move cursor up
                if cy > 0:
                    cy -= 1
                    cx = min(cx, len(buffer[cy]))
                elif cy == 0:
                    cx = 0
            elif char == Keys.DOWN:  # Move cursor down
                if cy < len(buffer) - 1:
                    cy += 1
                    cx = min(cx, len(buffer[cy]))
                elif cy == len(buffer) - 1:
                    cx = len(buffer[cy])
            elif char == Keys.LEFT:  # Move cursor left
                if cx > 0:
                    cx -= 1
                elif cy > 0:
                    cy -= 1
                    cx = len(buffer[cy])
            elif char == Keys.RIGHT:  # Move cursor right
                if cx < len(buffer[cy]):
                    cx += 1
                elif cy < len(buffer) - 1:
                    cy += 1
                    cx = 0
            elif char == Keys.BACKSPACE:  # Handle backspace
                if cx > 0:
                    buffer[cy] = buffer[cy][: cx - 1] + buffer[cy][cx:]
                    cx -= 1
                elif cy > 0:
                    prev_line = buffer.pop(cy)
                    cy -= 1
                    cx = len(buffer[cy])
                    buffer[cy] += prev_line
            elif char == Keys.ENTER:  # Handle Enter (newline)
                new_line = buffer[cy][cx:]
                buffer[cy] = buffer[cy][:cx]
                buffer.insert(cy + 1, new_line)
                cy += 1
                cx = 0
            elif char == Keys.CTRLD:
                break
            else:
                buffer[cy] = buffer[cy][:cx] + char + buffer[cy][cx:]
                cx += 1


class Prompt:
    """A class for prompting the user for input."""

    @staticmethod
    def text(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> TextPrompt:
        """Creates a text prompt where the user can input a text string."""
        return TextPrompt(message, schema, id)

    @staticmethod
    def password(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> PasswordPrompt:
        """Creates a password prompt where the user can input a text string masked with '*'."""
        return PasswordPrompt(message, schema, id)

    @staticmethod
    def confirm(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> ConfirmPrompt:
        """Creates a confirm prompt where the user can confirm an action, either yes or no."""
        return ConfirmPrompt(message, schema, id)

    @staticmethod
    def choice(
        message: str,
        choices: list[str],
        schema: Schema | None = None,
        id: str | None = None,
    ) -> ChoicePrompt:
        """Creates a choice prompt where the user can select from a list of choices."""
        return ChoicePrompt(message, choices, schema, id)

    @staticmethod
    def checkbox(
        message: str,
        choices: list[str],
        schema: Schema | None = None,
        id: str | None = None,
    ) -> CheckboxPrompt:
        """Creates a checkbox prompt where the user can select multiple choices from a list of choices."""
        return CheckboxPrompt(message, choices, schema, id)

    @staticmethod
    def number(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> NumberPrompt:
        """Creates a number prompt where the user can input a number."""
        return NumberPrompt(message, schema, id)

    @staticmethod
    def date(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> DatePrompt:
        """Creates a date prompt where the user can input a date."""
        return DatePrompt(message, schema, id)

    @staticmethod
    def editor(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> EditorPrompt:
        """Creates an editor prompt where the user can input multiple lines of text, along with syntax highlighting if specified."""
        return EditorPrompt(message, schema, id)
