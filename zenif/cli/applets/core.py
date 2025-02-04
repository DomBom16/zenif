from colorama import Fore, Style
from typing import Callable
import os
import sys

from ...log import Logger
from .decorators import alias, arg, flag, opt
from .exceptions import AppletError
from .formatters import HelpFormatter
from .installer import install_setup
from .parsers import parse_command_args


l = Logger({"log_line": {"format": []}})


class Applet:
    """
    A command-line interface (CLI) framework for defining and executing commands.

    This class provides functionality to register commands, set callbacks, and handle
    command-line arguments. It supports defining commands with arguments, options, and
    flags, as well as setting up callbacks for root, help, and pre-command execution.
    """

    def __init__(self):
        self.name = os.path.basename(sys.argv[0]) or "zenif-applet"
        self.commands: dict[str, Callable] = {}
        self.root_callback: Callable[[], any] | None = None
        self.before_command_callback: Callable[[str, list[str]], any] | None = None
        self.help_callback: Callable[[], any] | None = None

    def command(self, func: Callable) -> Callable:
        """Registers a function as a command."""
        self.commands[func.__name__] = func
        return func

    def root(self, func: Callable = None) -> Callable:
        """
        Decorator to set a callback for when no subcommand is passed.
        """

        def decorator(f: Callable) -> Callable:
            self.root_callback = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def before(self, func: Callable = None) -> Callable:
        """
        Decorator to set a callback that runs before any subcommand.
        """

        def decorator(f: Callable) -> Callable:
            self.before_command_callback = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def install(self, path: str) -> Callable:
        """Exposes a install command for the Applet."""
        return install_setup(self, path)

    def arg(self, name: str, *, help: str = "") -> Callable:
        """Decorator for a required positional argument."""
        return arg(name, help=help)

    def opt(self, name: str, *, default: any = None, help: str = "") -> Callable:
        """Decorator for an option (named parameter)."""
        return opt(name, default=default, help=help)

    def flag(self, name: str, *, help: str = "") -> Callable:
        """Decorator for a boolean flag."""
        return flag(name, help=help)

    def alias(self, name: str, to: str) -> Callable:
        """Decorator to set a shorthand alias for an option or flag."""
        return alias(name, alias=to)

    def help(self, func: Callable = None) -> Callable:
        """
        Decorator to set a callback for displaying help.
        """

        def decorator(f: Callable) -> Callable:
            self.help_callback = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def run(self, args: list[str] = None) -> None:
        """
        Executes the Applet with the given arguments.
        """

        if not args:
            args = sys.argv[1:]

        if not args:
            if self.root_callback:
                result = self.root_callback()
                if result is not None:
                    l.info(result)
            else:
                self.print_help()
            return

        if args[0] in ("-h", "--help"):
            if self.help_callback:
                result = self.help_callback()
                if result is not None:
                    l.info(result)
            self.print_help()
            return

        command_name = args[0]
        if command_name in self.commands:
            if any(arg in ("-h", "--help") for arg in args[1:]):
                if self.help_callback:
                    result = self.help_callback()
                    if result is not None:
                        l.info(result)
                self.print_command_help(command_name)
                return

            if self.before_command_callback:
                result = self.before_command_callback(command_name, args[1:])
                if result is not None:
                    l.info(result)
            try:
                command = self.commands[command_name]
                parsed_args = parse_command_args(command, args[1:])
                print(f"\x1b]2;{self.name} {command_name}\x07", end="")
                result = command(**parsed_args)
                if result is not None:
                    l.info(result)
            except AppletError as e:
                print(f"Error: {str(e)}")
                self.print_command_help(command_name)
        else:
            if self.help_callback:
                result = self.help_callback()
                if result is not None:
                    l.info(result)
            print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")
            self.print_help()

    def execute(self, command_name: str, args: list[str] | None = None) -> None:
        """
        Programmatically execute a registered command.
        """
        if args is None:
            args = []
        if any(arg in ("-h", "--help") for arg in args):
            if self.help_callback:
                result = self.help_callback()
                if result is not None:
                    l.info(result)
            self.print_command_help(command_name)
            return

        if command_name in self.commands:
            if self.before_command_callback:
                result = self.before_command_callback(command_name, args)
                if result is not None:
                    l.info(result)
            try:
                command = self.commands[command_name]
                parsed_args = parse_command_args(command, args)
                print(f"\x1b]2;{self.name} {command_name}\x07", end="")
                result = command(**parsed_args)
                if result is not None:
                    l.info(result)
            except AppletError as e:
                print(f"Error: {str(e)}")
                self.print_command_help(command_name)
        else:
            print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")
            self.print_help()

    def print_help(self) -> None:
        """Print the help text for the Applet."""
        help_text = HelpFormatter.format_cli_help(self.name, self.commands)
        print(help_text)

    def print_command_help(self, command_name: str) -> None:
        """Print the help text for a specific command."""
        if command_name in self.commands:
            help_text = HelpFormatter.format_command_help(
                command_name, self.commands[command_name]
            )
            print(help_text)
        else:
            print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")
