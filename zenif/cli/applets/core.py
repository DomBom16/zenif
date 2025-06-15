import os
import sys
from typing import Any, Callable

from colorama import Fore, Style

from ...log import Logger
from .commands import handle_help_flags
from .commands import resolve_command as rescmd
from .commands import run_command as execmd
from .error_handlers import handle_help_request
from .help import Help
from .installer import install_setup
from .parameters import alias as _alias
from .parameters import arg as _arg
from .parameters import flag as _flag
from .parameters import opt as _opt
from .parser import HELP_FLAGS

L = Logger({"log_line": {"format": []}})


class Applet:
    """
    A command-line interface (CLI) framework for defining and executing commands.

    This class provides functionality to register commands, set callbacks, and handle
    command-line arguments. It supports defining commands with arguments, options, and
    flags, as well as setting up callbacks for root, help, and pre-command execution.
    """

    def __init__(self, single: bool = False):
        """
        Initialize the Applet CLI framework.

        Args:
            single: Whether the applet operates in single command mode (default: False)
        """
        # Strip the file extension from the basename
        self.name = os.path.basename(sys.argv[0]) or "zenif-applet"
        self.name = os.path.splitext(self.name)[0]

        self.commands: dict[str, Callable] = {}
        self.aliases: dict[str, str] = {}

        self._single = single
        self._single_cmd: Callable[[], Any] | None = None

        self._root: Callable[[], Any] | None = None
        self._before: Callable[[str, list[str]], Any] | None = None
        self._after: Callable[[str, list[str]], Any] | None = None
        self._help: Callable[[], Any] | None = None

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
            self._root = f
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
            self._before = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def after(self, func: Callable | None = None) -> Callable:
        """
        Decorator to set a callback that runs after any subcommand.
        """

        def decorator(f: Callable) -> Callable:
            self._after = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def install(self, path: str) -> Callable:
        """Exposes a install command for the Applet."""
        return install_setup(self, path)

    def _install_help(self) -> Callable:
        app = self

        @app.command
        def help() -> None:
            """Show this help menu"""
            if self._help:
                result = self._help()
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
            self._help = f
            return f

        if func is None:
            return decorator
        return decorator(func)

    def single(self, func: Callable | None = None) -> Callable:
        """
        Decorator to set a callback for the main command in single command mode.
        """

        def decorator(f: Callable) -> Callable:
            self._single_cmd = f
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

        # SINGLE COMMAND MODE
        if self._single:
            # If help is requested, show help for the main command
            if args and handle_help_flags(
                args, self._help, self.name, self._single_cmd
            ):
                if not self._single_cmd:
                    self.print_help()
                return

            # Execute the main command with all args
            if self._single_cmd:
                # Execute the main command with error handling
                execmd(
                    self._single_cmd,
                    args,
                    self.name,
                    self.name,
                    self._help,
                    self._before,
                    self._after,
                    {self.name: self._single_cmd},
                )
            else:
                print(
                    f"{Fore.YELLOW}No main command defined for single command mode{Style.RESET_ALL}"
                )
            return

        # MULTI COMMAND MODE
        # If help is explicitly requested with -h or --help as the first argument, show general help and exit
        if args and args[0] in HELP_FLAGS:
            handle_help_request(self._help, "root", self._root)
            self.print_help()
            return

        # Handle no arguments - run root callback if defined
        if not args:
            if self._root:  # Use root_callback consistently
                execmd(
                    self._root,
                    args,
                    self.name,
                    "root",
                    self._help,
                    None,
                    None,
                    {"root": self._root},
                )
            else:
                self.print_help()
            return

        # Root function direct calling detection
        # Case 1: First argument starts with - (a flag/option)
        # Case 2: First argument contains = (a key-value pair)
        # Case 3: Command name matches the root function's name
        root_func_name = (
            getattr(self._root, "_primary_name", "root") if self._root else None
        )

        if self._root and (
            args[0].startswith("-")
            or "=" in args[0]
            or (root_func_name and args[0] == root_func_name)
        ):
            # If the command name matches the root function name, remove it from args
            if root_func_name and args[0] == root_func_name:
                args = args[1:]

            # Check for help flags specifically in root command arguments
            if handle_help_flags(args, self._help, "root", self._root):
                return

            # Execute the root command and return
            execmd(
                self._root,
                args,
                self.name,
                "root",
                self._help,
                None,
                None,
                {"root": self._root},
            )
            return

        command_name = args[0]
        # Resolve the alias using our utility function
        resolved_command = rescmd(command_name, self.commands, self.aliases)

        if resolved_command != command_name:
            command_name = resolved_command
        elif command_name not in self.commands:
            if self._help:
                result = self._help()
                if result is not None:
                    L.info(result)
            print(f"{Fore.YELLOW}Command {args[0]} not found{Style.RESET_ALL}")
            self.print_help()
            return

        # Handle command-specific help flag properly
        if len(args) > 1 and any(arg in HELP_FLAGS for arg in args[1:]):
            handle_help_request(
                self._help, command_name, self.commands.get(command_name)
            )
            return

        # Execute the command with full error handling
        execmd(
            self.commands[command_name],
            args[1:],
            self.name,
            command_name,
            self._help,
            self._before,
            self._after,
            self.commands,
        )

    def execute(self, command_name: str, args: list[str] | None = None) -> None:
        """
        Programmatically execute a registered command.
        """

        if args is None:
            args = []
        if any(arg in HELP_FLAGS for arg in args):
            handle_help_request(
                self._help,
                command_name,
                self.commands.get(command_name)
                if command_name in self.commands
                else self._root,
            )
            return

        # Check if executing the root command
        if command_name == "root" or (
            self._root and command_name == getattr(self._root, "_primary_name", None)
        ):
            if self._root:
                # Execute the root command with error handling
                execmd(
                    self._root,
                    args,
                    self.name,
                    "root",
                    self._help,
                    self._before,
                    self._after,
                    {"root": self._root},
                )
                return

        # Resolve aliases if needed.
        if command_name not in self.commands and command_name in self.aliases:
            command_name = self.aliases[command_name]

        if command_name in self.commands:
            # Execute the command with full error handling
            execmd(
                self.commands[command_name],
                args,
                self.name,
                command_name,
                self._help,
                self._before,
                self._after,
                self.commands,
            )
        else:
            print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")
            self.print_help()

    def print_help(self) -> None:
        """Print the help text for the Applet."""
        if self._single and self._single_cmd:
            # In single mode, just show help for the main command
            help_text = Help.cmd(self.name, self._single_cmd)
            print(help_text)
        else:
            # For multi mode, iterate over the primary command names
            help_text = Help.cli(self.name, self.commands)
            print(help_text)

    def print_command_help(self, command_name: str) -> None:
        """Print the help text for a specific command."""
        if command_name in self.commands:
            help_text = Help.cmd(command_name, self.commands[command_name])
            print(help_text)
        else:
            print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")
