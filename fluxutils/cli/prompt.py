import sys
from colorama import init, Fore, Style
import getpass

init(autoreset=True)


class BasePrompt:
    def __init__(self, message: str):
        self.message = message

    def ask(self) -> any:
        raise NotImplementedError


class TextPrompt(BasePrompt):
    def __init__(self, message: str):
        super().__init__(message)
        self._default: str | None = None

    def default(self, value: str) -> "TextPrompt":
        self._default = value
        return self

    def ask(self) -> str:
        default_text = (
            f" {Style.DIM}({self._default}){Style.NORMAL}" if self._default else ""
        )
        while True:
            user_input = input(
                f"{Fore.GREEN}? {Fore.CYAN}{self.message}{default_text}{Fore.CYAN}: {Fore.YELLOW}"
            )
            user_input = user_input or self._default
            if not user_input:
                user_input = ""
            print(
                f"\033[1A\033[2K{Fore.GREEN}? {Fore.CYAN}{self.message}: {Fore.YELLOW}{user_input}{Fore.RESET}"
            )
            if user_input:
                return user_input
            print(f"\033[2A")


class PasswordPrompt(BasePrompt):
    def ask(self) -> str:
        while True:
            password = getpass.getpass(
                f"{Fore.GREEN}? {Fore.CYAN}{self.message}: {Fore.YELLOW}"
            )
            print(
                f"\033[1A\033[2K{Fore.GREEN}? {Fore.CYAN}{self.message}: {Fore.YELLOW}{'*' * len(password)}{Fore.RESET}"
            )
            if password:
                return password
            print(f"\033[2A")


class ConfirmPrompt(BasePrompt):
    def __init__(self, message: str):
        super().__init__(message)
        self._default: bool | None = None

    def default(self, value: bool) -> "ConfirmPrompt":
        self._default = value
        return self

    def ask(self) -> bool:
        default_text = (
            " (y/N)"
            if self._default is False
            else " (Y/n)" if self._default is True else " (y/n)"
        )
        print(
            f"{Fore.GREEN}? {Fore.CYAN}{self.message}{Style.DIM}{default_text}{Style.NORMAL}: ",
            end="",
            flush=True,
        )
        while True:
            key = self._get_key().lower()

            if key in ("y", "n"):
                print(
                    f"\r\033[2K{Fore.GREEN}? {Fore.CYAN}{self.message}: {Fore.YELLOW}{"Yes" if key == "y" else "No"}{Fore.RESET}"
                )
                return key == "y"
            elif key == "\r" and self._default:
                print(
                    f"\r\033[2K{Fore.GREEN}? {Fore.CYAN}{self.message}: {Fore.YELLOW}{"Yes" if self._default else "No"}{Fore.RESET}"
                )
                return self._default

    @staticmethod
    def _get_key():
        if sys.platform.startswith("win"):
            import msvcrt

            return msvcrt.getch().decode("utf-8")
        else:
            import termios, tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch


class ChoicePrompt(BasePrompt):
    def __init__(self, message: str, choices: list[str]):
        super().__init__(message)
        self.choices = choices

    def ask(self) -> str:
        print(
            f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n{Style.DIM}  Use Up/Down to navigate and Enter to select"
        )
        current = 0

        def print_choices():
            for i, choice in enumerate(self.choices):
                if i == current:
                    print(f"{Fore.YELLOW}{Style.NORMAL}> {choice}{Fore.RESET}")
                else:
                    print(f"{Fore.YELLOW}{Style.DIM}  {choice}")

        print_choices()
        while True:
            key = self._get_key()
            if key == "\r":  # Enter key
                for _ in range(len(self.choices) + 2):
                    print(f"\033[1A\033[2K", end="")
                print(
                    f"{Fore.GREEN}? {Fore.CYAN}{self.message}: {Fore.YELLOW}{self.choices[current]}"
                )
                return self.choices[current]
            elif key == "\x1b[A" and current > 0:  # Up arrow
                current -= 1
            elif key == "\x1b[B" and current < len(self.choices) - 1:  # Down arrow
                current += 1
            else:
                continue

            # Clear the output and reprint choices
            print(f"\033[{len(self.choices)}A\033[J", end="")
            print_choices()

    @staticmethod
    def _get_key():
        if sys.platform.startswith("win"):
            import msvcrt

            return msvcrt.getch().decode("utf-8")
        else:
            import termios, tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    ch += sys.stdin.read(2)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch


class CheckboxPrompt(BasePrompt):
    def __init__(self, message: str, choices: list[str]):
        super().__init__(message)
        self.choices = choices

    def ask(self) -> list[str]:
        selected = [False] * len(self.choices)
        current = 0
        first_render = True

        def print_choices():
            nonlocal first_render
            if not first_render:
                # Move cursor up to the start of the prompt
                print(f"\033[{len(self.choices) + 2}A", end="")
            else:
                first_render = False

            # Clear from cursor to end of screen
            print("\033[J", end="")

            print(
                f"{Fore.GREEN}? {Fore.CYAN}{self.message}:{Fore.RESET}\n  {Style.DIM}Use Up/Down to navigate, Space to select, and Enter to confirm"
            )
            for i, (choice, is_selected) in enumerate(zip(self.choices, selected)):
                if i == current:
                    print(f"{Fore.YELLOW}{Style.DIM}X{Style.NORMAL}", end="")
                else:
                    print(f"{Fore.YELLOW} ", end="")
                print(
                    f"\r{f"{Fore.YELLOW}X" if is_selected else '\033[1C'} {Fore.YELLOW}{Style.DIM}{choice}{Fore.RESET}"
                )

        print_choices()
        while True:
            key = self._get_key()
            if key == " ":
                selected[current] = not selected[current]
                print_choices()
            elif key == "\r":
                for _ in range(len(self.choices) + 2):
                    print(f"\033[1A\033[2K", end="")
                selected_choices = [
                    choice
                    for choice, is_selected in zip(self.choices, selected)
                    if is_selected
                ]
                print(
                    f"{Fore.GREEN}? {Fore.CYAN}{self.message}: {Fore.YELLOW}{", ".join(selected_choices)}"
                )
                return selected_choices
            elif key == "\x1b[A" and current > 0:
                current -= 1
                print_choices()
            elif key == "\x1b[B" and current < len(self.choices) - 1:
                current += 1
                print_choices()

    @staticmethod
    def _get_key():
        if sys.platform.startswith("win"):
            import msvcrt

            return msvcrt.getch().decode("utf-8")
        else:
            import termios, tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    ch += sys.stdin.read(2)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch


class NumberPrompt(BasePrompt):
    def __init__(self, message: str):
        super().__init__(message)
        self._min: float | None = None
        self._max: float | None = None
        self._default: float | None = None

    def default(self, value: float) -> "ConfirmPrompt":
        self._default = value
        return self

    def min(self, value: float) -> "NumberPrompt":
        self._min = value
        return self

    def max(self, value: float) -> "NumberPrompt":
        self._max = value
        return self

    def ask(self) -> float:
        while True:
            try:
                default_text = (
                    f" {Style.DIM}({self._default}){Style.NORMAL}"
                    if self._default
                    else ""
                )
                user_input = input(
                    f"{Fore.GREEN}? {Fore.CYAN}{self.message}{default_text}: {Fore.YELLOW}"
                ) or (self._default if self._default else "")
                value = float(user_input)
                if (self._min is not None and value < self._min) or (
                    self._max is not None and value > self._max
                ):
                    raise ValueError
                print(
                    f"\033[1A\033[2K{Fore.GREEN}? {Fore.CYAN}{self.message}: {Fore.YELLOW}{user_input}"
                )
                return value
            except ValueError:
                if self._min is not None and self._max is not None:
                    print(
                        f"{Fore.RED}Please enter a number between {self._min} and {self._max}.{Fore.RESET}"
                    )
                elif self._min is not None:
                    print(
                        f"{Fore.RED}Please enter a number greater than or equal to {self._min}.{Fore.RESET}"
                    )
                elif self._max is not None:
                    print(
                        f"{Fore.RED}Please enter a number less than or equal to {self._max}.{Fore.RESET}"
                    )
                else:
                    print(f"{Fore.RED}Please enter a valid number.{Fore.RESET}")


class Prompt:
    @staticmethod
    def text(message: str) -> TextPrompt:
        return TextPrompt(message)

    @staticmethod
    def password(message: str) -> PasswordPrompt:
        return PasswordPrompt(message)

    @staticmethod
    def confirm(message: str) -> ConfirmPrompt:
        return ConfirmPrompt(message)

    @staticmethod
    def choice(message: str, choices: list[str]) -> ChoicePrompt:
        return ChoicePrompt(message, choices)

    @staticmethod
    def checkbox(message: str, choices: list[str]) -> CheckboxPrompt:
        return CheckboxPrompt(message, choices)

    @staticmethod
    def number(message: str) -> NumberPrompt:
        return NumberPrompt(message)
