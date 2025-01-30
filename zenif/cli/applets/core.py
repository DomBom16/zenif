from typing import Callable
import sys
from .parsers import parse_command_args
from .formatters import HelpFormatter, OutputFormatter
from .exceptions import CLIError

from ...log import Logger
from ...decorators import deprecated

logger = Logger({"log_line": {"format": []}})


class CLI:
    def __init__(self, name: str = "cli"):
        """The CLI class for creating interactive command-line applications.

        Args:
            name (str, optional): The name of the CLI. Defaults to "cli".
        """
        self.name = name
        self.commands: dict[str, Callable] = {}

    def command(self, func: Callable) -> Callable:
        """Decorator to register a function as a CLI command."""
        self.commands[func.__name__] = func
        return func

    def run(self, args: list[str] = None) -> None:
        """Run the CLI application."""
        if not args:
            args = sys.argv[1:]

        if not args or args[0] in ("-h", "--help"):
            self.print_help()
            return

        command_name = args[0]
        if command_name in self.commands:
            try:
                # fetch command
                command = self.commands[command_name]
                # parse arguments
                parsed_args = parse_command_args(command, args[1:])
                # change terminal title
                print(f"\x1b]2;{self.name} {command_name}\x07", end="")
                # run command
                result = command(**parsed_args)
                if result is not None:
                    logger.info(result)
            except CLIError as e:
                print(f"Error: {str(e)}")
                self.print_command_help(command_name)
        else:
            print(f"Unknown command: {command_name}")
            self.print_help()

    def print_help(self) -> None:
        """Print help information for the entire CLI."""
        help_text = HelpFormatter.format_cli_help(self.name, self.commands)
        print(help_text)

    def print_command_help(self, command_name: str) -> None:
        """Print help information for a specific command."""
        if command_name in self.commands:
            help_text = HelpFormatter.format_command_help(
                command_name, self.commands[command_name]
            )
            print(help_text)
        else:
            print(f"Unknown command: {command_name}")

    @deprecated(expected_removal="v1.0.0")
    def echo(self, message: any) -> None:
        """Print a formatted message to the console. Works with lists, tuples, and dictionaries. Other formats are printed as is."""
        formatted_output = OutputFormatter.format_output(message)
        print(formatted_output)
