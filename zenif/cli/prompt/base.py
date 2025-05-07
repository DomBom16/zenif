import sys

from colorama import Fore, Style

from ...constants import Cursor
from ...schema import Schema
from ...utils import get_key


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
                is_valid, errors, _ = self.schema.validate(
                    {self.id: value}, partial=True
                )
                if not is_valid:
                    # Expect errors to be a tuple (ErrorClass, message)
                    error_tuple = errors.get(
                        self.id, [("ValidationError", "Invalid input")]
                    )[0]
                    return error_tuple[1].rstrip(".")
            elif self.field:
                self.field.validate(value)
            return None
        except Exception as e:
            return str(e)

    @staticmethod
    def _get_key() -> str:
        return get_key()

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
            options = [option.lower() for option in options]
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
                    f" {Fore.CYAN}{Style.DIM}[{''.join(options)}]{Style.RESET_ALL}"
                )
        sys.stdout.write(f" {Fore.YELLOW}{value}")
        if error:
            sys.stdout.write(f"  {Fore.RED}{error}{Cursor.left(2 + len(error))}")

        sys.stdout.flush()
