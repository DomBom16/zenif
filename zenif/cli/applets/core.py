from typing import Callable
import sys
from .parsers import parse_command_args
from .formatters import HelpFormatter, OutputFormatter
from .exceptions import CLIError

from ...log import Logger
from ...decorators import deprecated

logger = Logger({"log_line": {"format": []}})


class CLI:
    def __init__(self, name: str | None = None):
        """The CLI class for creating interactive command-line applications.

        Args:
            name (str, optional): The name of the CLI.
        """
        self.name = name or "zenif-cli"
        self.commands: dict[str, Callable] = {}
        self.root_callback: Callable[[], any] | None = None
        self.before_command_callback: Callable[[str, list[str]], any] | None = None
        self.help_callback: Callable[[], any] | None = None

    def command(self, func: Callable) -> Callable:
        """Register a function as a CLI command."""
        self.commands[func.__name__] = func
        return func

    def root(self, func: Callable = None) -> Callable:
        """
        Set a callback to run when no subcommand is passed.
        The return value will be logged if not None.
        Can be used with or without parentheses.
        """

        def decorator(f: Callable) -> Callable:
            self.root_callback = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def before(self, func: Callable = None) -> Callable:
        """
        Set a callback to run before any subcommand is executed.
        The callback receives the command name and the remaining arguments.
        Its return value will be logged if not None.
        Can be used with or without parentheses.
        """

        def decorator(f: Callable) -> Callable:
            self.before_command_callback = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def help(self, func: Callable = None) -> Callable:
        """
        Set a callback to run whenever help is shown.
        This is triggered when '-h'/'--help' is passed, or when an unknown command is used.
        Its return value will be logged if not None.
        Can be used with or without parentheses.
        """

        def decorator(f: Callable) -> Callable:
            self.help_callback = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def run(self, args: list[str] = None) -> None:
        """Run the CLI application."""
        if not args:
            args = sys.argv[1:]

        # If no arguments are provided, invoke the root callback if set.
        if not args:
            if self.root_callback:
                result = self.root_callback()
                if result is not None:
                    logger.info(result)
            else:
                self.print_help()
            return

        # If the first argument is a help flag, process global help.
        if args[0] in ("-h", "--help"):
            if self.help_callback:
                result = self.help_callback()
                if result is not None:
                    logger.info(result)
            self.print_help()
            return

        command_name = args[0]
        if command_name in self.commands:
            # Check if any help flag is present among the subcommand arguments.
            if any(arg in ("-h", "--help") for arg in args[1:]):
                if self.help_callback:
                    result = self.help_callback()
                    if result is not None:
                        logger.info(result)
                self.print_command_help(command_name)
                return

            # Run the before_command callback (if registered) before executing the subcommand.
            if self.before_command_callback:
                result = self.before_command_callback(command_name, args[1:])
                if result is not None:
                    logger.info(result)
            try:
                # Fetch command
                command = self.commands[command_name]
                # Parse arguments
                parsed_args = parse_command_args(command, args[1:])
                # Change terminal title
                print(f"\x1b]2;{self.name} {command_name}\x07", end="")
                # Run command
                result = command(**parsed_args)
                if result is not None:
                    logger.info(result)
            except CLIError as e:
                print(f"Error: {str(e)}")
                self.print_command_help(command_name)
        else:
            if self.help_callback:
                result = self.help_callback()
                if result is not None:
                    logger.info(result)
            print(f"Unknown command: {command_name}")
            self.print_help()

    def execute(self, command_name: str, args: list[str] | None = None) -> None:
        """Programatically execute a registered command.

        Args:
            command_name (str): The name of the command to execute.
            args (list[str] | None, optional): The arguments to pass to the command. Defaults to None.
        """
        if args is None:
            args = []
        # Check for help flags in the provided arguments.
        if any(arg in ("-h", "--help") for arg in args):
            if self.help_callback:
                result = self.help_callback()
                if result is not None:
                    logger.info(result)
            self.print_command_help(command_name)
            return

        if command_name in self.commands:
            if self.before_command_callback:
                result = self.before_command_callback(command_name, args)
                if result is not None:
                    logger.info(result)
            try:
                command = self.commands[command_name]
                parsed_args = parse_command_args(command, args)
                print(f"\x1b]2;{self.name} {command_name}\x07", end="")
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
        """
        Print a formatted message to the console.
        Works with lists, tuples, and dictionaries. Other formats are printed as is.
        """
        formatted_output = OutputFormatter.format_output(message)
        print(formatted_output)
