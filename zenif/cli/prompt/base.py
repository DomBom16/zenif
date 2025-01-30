from ...schema import Schema
from ...constants import Keys, Cursor

import signal
import sys
from colorama import init, Fore, Style

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
        default: str | None = None,
        options: list[str] | None = None,
        default_option: str | None = None,
        error: str | None = None,
    ):
        sys.stdout.write(
            f"{Cursor.lclear()}\r{Fore.GREEN}? {Fore.CYAN}{prompt}{Fore.RESET}"
        )
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
        sys.stdout.write(f"{Fore.CYAN} {Fore.YELLOW}{value}")
        if error:
            sys.stdout.write(f"  {Fore.RED}{error}{Cursor.left(2 + len(error))}")

        sys.stdout.flush()
