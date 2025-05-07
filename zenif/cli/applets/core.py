import os
import sys
from typing import Any, Callable

from colorama import Fore, Style

from ...log import Logger
from .exceptions import AppletError
from .formatters import HelpFormatter
from .installer import install_setup
from .parameters import _alias, _arg, _flag, _opt
from .parser import parse_command_args

L = Logger({"log_line": {"format": []}})


class Applet:
    """
    A command-line interface (CLI) framework for defining and executing commands.

    This class provides functionality to register commands, set callbacks, and handle
    command-line arguments. It supports defining commands with arguments, options, and
    flags, as well as setting up callbacks for root, help, and pre-command execution.
    """

    def __init__(self, mode: str = "multi"):
        """
        Initialize the Applet CLI framework.

        Args:
            mode: The mode of operation - "multi" (default) for subcommands or
                 "single" for a single command CLI
        """
        self.name = os.path.basename(sys.argv[0]) or "zenif-applet"
        self.mode = mode  # 'multi' or 'single'

        self.commands: dict[str, Callable] = {}
        self.aliases: dict[str, str] = {}

        self.root_callback: Callable[[], Any] | None = None
        self.main_command: Callable[[], Any] | None = None
        self.before_callback: Callable[[str, list[str]], Any] | None = None
        self.help_callback: Callable[[], Any] | None = None

    def command(
        self, func: Callable | None = None, *, aliases: list[str] | None = None
    ) -> Callable:
        """
        Decorator to register a function as a command.
        Optionally accepts an `aliases` list to register alternate names.
        """

        def decorator(f: Callable) -> Callable:
            primary_name = f.__name__
            # Check for collisions in primary names or aliases.
            if primary_name in self.commands or primary_name in self.aliases:
                raise Exception(f"Command '{primary_name}' is already registered.")
            self.commands[primary_name] = f

            # Store metadata on the function (could be useful for help formatting)
            f._primary_name = primary_name
            f._aliases = aliases or []

            if aliases:
                for alias in aliases:
                    if alias in self.commands or alias in self.aliases:
                        raise Exception(
                            f"Alias '{alias}' is already registered as a command or alias."
                        )
                    self.aliases[alias] = primary_name
            return f

        if func is None:
            return decorator
        return decorator(func)

    def root(self, func: Callable | None = None) -> Callable:
        """
        Decorator to set a callback for when no subcommand is passed.
        Can also be called directly with arguments.
        """

        def decorator(f: Callable) -> Callable:
            self.root_callback = f  # Use root_callback consistently
            # Attach CLI metadata similar to command decorator
            f._primary_name = f.__name__
            if not hasattr(f, "_aliases"):
                f._aliases = []
            if not hasattr(f, "_cli_params"):
                f._cli_params = {}
            return f

        if func is None:
            return decorator
        return decorator(func)

    def before(self, func: Callable | None = None) -> Callable:
        """
        Decorator to set a callback that runs before any subcommand.
        """

        def decorator(f: Callable) -> Callable:
            self.before_callback = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def install(self, path: str) -> Callable:
        """Exposes a install command for the Applet.

        _**NOTE:** install is not intended for production use. Only use for development._
        """
        return install_setup(self, path)

    def _install_help(self) -> Callable:
        app = self

        @app.command
        def help() -> None:
            """Show this help menu"""
            if self.help_callback:
                result = self.help_callback()
                if result is not None:
                    L.info(result)
            self.print_help()
            return

        return help

    def arg(self, name: str, *, help: str = "") -> Callable:
        """Decorator for a required positional argument."""
        return _arg(name, help=help)

    def opt(self, name: str, *, default: Any = None, help: str = "") -> Callable:
        """Decorator for an option (named parameter)."""
        return _opt(name, default=default, help=help)

    def flag(self, name: str, *, help: str = "") -> Callable:
        """Decorator for a boolean flag."""
        return _flag(name, help=help)

    def alias(self, name: str, to: str) -> Callable:
        """Decorator to set a shorthand alias for an option or flag."""
        return _alias(name, alias=to)

    def help(self, func: Callable | None = None) -> Callable:
        """
        Decorator to set a callback for displaying help.
        """

        def decorator(f: Callable) -> Callable:
            self.help_callback = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def main(self, func: Callable | None = None) -> Callable:
        """
        Decorator to set a callback for the main command in single command mode.
        """

        def decorator(f: Callable) -> Callable:
            self.main_command = f
            # Attach CLI metadata similar to command decorator
            f._primary_name = "main"
            if not hasattr(f, "_aliases"):
                f._aliases = []
            if not hasattr(f, "_cli_params"):
                f._cli_params = {}
            return f

        if func is None:
            return decorator
        return decorator(func)

    def run(self, args: list[str] | None = None) -> None:
        self._install_help()

        if not args:
            args = sys.argv[1:]

        help_flags = ["-h", "--help"]

        # SINGLE COMMAND MODE
        if self.mode == "single":
            # If help is requested, show help for the main command
            if args and any(arg in help_flags for arg in args):
                if self.help_callback:
                    result = self.help_callback()
                    if result is not None:
                        L.info(result)
                if self.main_command:
                    print(
                        f"{HelpFormatter.format_command_help(self.name, self.main_command)}\n"
                    )
                else:
                    self.print_help()
                return

            # Execute the main command with all args
            if self.main_command:
                try:
                    if self.before_callback:
                        result = self.before_callback(self.name, args)
                        if result is not None:
                            L.info(result)

                    parsed_args = parse_command_args(self.main_command, args)
                    print(f"\x1b]2;{self.name} {' '.join(args)}\x07", end="")
                    result = self.main_command(**parsed_args)
                    if result is not None:
                        L.info(result)
                except AppletError as e:
                    if str(e) == "Help requested":
                        if self.help_callback:
                            result = self.help_callback()
                            if result is not None:
                                L.info(result)
                        print(
                            f"{HelpFormatter.format_command_help(self.name, self.main_command)}\n"
                        )
                        return
                    print(f"Error: {str(e)}")
                    print(
                        f"{HelpFormatter.format_command_help(self.name, self.main_command)}\n"
                    )
            else:
                print(
                    f"{Fore.YELLOW}No main command defined for single command mode{Style.RESET_ALL}"
                )
            return

        # MULTI COMMAND MODE (original behavior)
        # If help is explicitly requested with -h or --help as the first argument, show general help and exit
        if args and args[0] in help_flags:
            if self.help_callback:
                result = self.help_callback()
                if result is not None:
                    L.info(result)
            if self.root_callback:  # Use root_callback consistently
                print(
                    f"{HelpFormatter.format_command_help('root', self.root_callback)}\n"
                )
            self.print_help()
            return

        # Handle no arguments - run root callback if defined
        if not args:
            if self.root_callback:  # Use root_callback consistently
                parsed_args = parse_command_args(self.root_callback, args)
                result = self.root_callback(**parsed_args)
                if result is not None:
                    L.info(result)
            else:
                self.print_help()
            return

        # Root function direct calling detection
        # Case 1: First argument starts with - (a flag/option)
        # Case 2: First argument contains = (a key-value pair)
        # Case 3: Command name matches the root function's name
        root_func_name = (
            getattr(self.root_callback, "_primary_name", "root")
            if self.root_callback
            else None
        )

        if self.root_callback and (
            args[0].startswith("-")
            or "=" in args[0]
            or (root_func_name and args[0] == root_func_name)
        ):
            # If the command name matches the root function name, remove it from args
            if root_func_name and args[0] == root_func_name:
                args = args[1:]

            # Check for help flags specifically in root command arguments
            if any(arg in help_flags for arg in args):
                if self.help_callback:
                    result = self.help_callback()
                    if result is not None:
                        L.info(result)
                print(
                    f"{HelpFormatter.format_command_help('root', self.root_callback)}\n"
                )
                return

            try:
                parsed_args = parse_command_args(self.root_callback, args)
                result = self.root_callback(**parsed_args)
                if result is not None:
                    L.info(result)
                return
            except AppletError as e:
                if str(e) == "Help requested":
                    if self.help_callback:
                        result = self.help_callback()
                        if result is not None:
                            L.info(result)
                    print(
                        f"{HelpFormatter.format_command_help('root', self.root_callback)}\n"
                    )
                    return
                print(f"Error: {str(e)}")
                self.print_command_help("root")
                return

        command_name = args[0]
        # Resolve the alias: if the command name is not primary, check aliases.
        if command_name not in self.commands:
            if command_name in self.aliases:
                # Use the primary command name even if an alias was given.
                command_name = self.aliases[command_name]
            else:
                if self.help_callback:
                    result = self.help_callback()
                    if result is not None:
                        L.info(result)
                print(f"{Fore.YELLOW}Command {args[0]} not found{Style.RESET_ALL}")
                self.print_help()
                return

        # Handle command-specific help flag properly
        if len(args) > 1 and any(arg in help_flags for arg in args[1:]):
            if self.help_callback:
                result = self.help_callback()
                if result is not None:
                    L.info(result)
            self.print_command_help(command_name)
            return

        if self.before_callback:
            result = self.before_callback(command_name, args[1:])
            if result is not None:
                L.info(result)
        try:
            command = self.commands[command_name]
            # Check explicitly for help flags before parsing args
            if any(arg in help_flags for arg in args[1:]):
                if self.help_callback:
                    result = self.help_callback()
                    if result is not None:
                        L.info(result)
                self.print_command_help(command_name)
                return

            parsed_args = parse_command_args(command, args[1:])
            primary_name = getattr(command, "_primary_name", command_name)
            print(
                f"\x1b]2;{self.name} {primary_name} {' '.join(args[1:])}\x07",
                end="",
            )
            result = command(**parsed_args)
            if result is not None:
                L.info(result)
        except AppletError as e:
            if str(e) == "Help requested":
                if self.help_callback:
                    result = self.help_callback()
                    if result is not None:
                        L.info(result)
                self.print_command_help(command_name)
                return
            print(f"Error: {str(e)}")
            self.print_command_help(command_name)

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
                    L.info(result)
            self.print_command_help(command_name)
            return

        # Check if executing the root command
        if command_name == "root" or (
            self.root_callback
            and command_name == getattr(self.root_callback, "_primary_name", None)
        ):
            if self.root_callback:
                if self.before_callback:
                    result = self.before_callback("root", args)
                    if result is not None:
                        L.info(result)
                try:
                    parsed_args = parse_command_args(self.root_callback, args)
                    print(f"\x1b]2;{self.name} {' '.join(args)}\x07", end="")
                    result = self.root_callback(**parsed_args)
                    if result is not None:
                        L.info(result)
                    return
                except AppletError as e:
                    if str(e) == "Help requested":
                        if self.help_callback:
                            result = self.help_callback()
                            if result is not None:
                                L.info(result)
                        self.print_command_help("root")
                        return
                    print(f"Error: {str(e)}")
                    if self.root_callback:
                        self.print_command_help("root")
                    return

        # Resolve aliases if needed.
        if command_name not in self.commands and command_name in self.aliases:
            command_name = self.aliases[command_name]

        if command_name in self.commands:
            if self.before_callback:
                result = self.before_callback(command_name, args)
                if result is not None:
                    L.info(result)
            try:
                command = self.commands[command_name]
                parsed_args = parse_command_args(command, args)
                primary_name = getattr(command, "_primary_name", command_name)
                print(f"\x1b]2;{self.name} {primary_name}\x07", end="")
                result = command(**parsed_args)
                if result is not None:
                    L.info(result)
            except AppletError as e:
                if str(e) == "Help requested":
                    if self.help_callback:
                        result = self.help_callback()
                        if result is not None:
                            L.info(result)
                    self.print_command_help(command_name)
                    return
                print(f"Error: {str(e)}")
                self.print_command_help(command_name)
        else:
            print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")
            self.print_help()

    def print_help(self) -> None:
        """Print the help text for the Applet."""
        if self.mode == "single" and self.main_command:
            # In single mode, just show help for the main command
            help_text = HelpFormatter.format_command_help(self.name, self.main_command)
            print(help_text)
        else:
            # For multi mode, iterate over the primary command names
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
