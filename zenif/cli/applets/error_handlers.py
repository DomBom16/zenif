from typing import Callable, Optional

from colorama import Fore, Style

from ...log import Logger
from .exceptions import (
    AppletCommandError,
    AppletError,
    AppletHelpError,
    AppletNotFoundError,
    AppletParseError,
    AppletValidationError,
)
from .help import Help

L = Logger({"log_line": {"format": []}})


def handle_help_request(
    help_callback: Optional[Callable] = None,
    command_name: str = "root",
    command: Optional[Callable] = None,
) -> None:
    """
    Handle help requests by displaying appropriate help information.

    Args:
        help_callback: Optional callback function for help requests
        command_name: The name of the command (default: "root")
        command: The command function to display help for
    """
    if help_callback:
        result = help_callback()
        if result is not None:
            L.info(result)

    if command:
        print(f"{Help.cmd(command_name, command)}\n")
    else:
        print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")


def handle_validation_error(
    error: AppletValidationError, command_name: str, commands: dict = None
) -> None:
    """
    Handle validation errors by displaying the error message and command help.

    Args:
        error: The validation error
        command_name: The name of the command
        commands: Dictionary of available commands
    """
    print(f"Validation Error: {str(error)}")
    if commands and command_name in commands:
        print(f"{Help.cmd(command_name, commands[command_name])}\n")
    else:
        print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")


def handle_not_found_error(
    error: AppletNotFoundError, command_name: str, commands: dict = None
) -> None:
    """
    Handle not found errors by displaying the error message and command help.

    Args:
        error: The not found error
        command_name: The name of the command
        commands: Dictionary of available commands
    """
    print(f"Not Found: {str(error)}")
    if commands and command_name in commands:
        print(f"{Help.cmd(command_name, commands[command_name])}\n")
    else:
        print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")


def handle_parse_error(
    error: AppletParseError, command_name: str, commands: dict = None
) -> None:
    """
    Handle parse errors by displaying the error message and command help.

    Args:
        error: The parse error
        command_name: The name of the command
        commands: Dictionary of available commands
    """
    print(f"Parse Error: {str(error)}")
    if commands and command_name in commands:
        print(f"{Help.cmd(command_name, commands[command_name])}\n")
    else:
        print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")


def handle_command_error(
    error: AppletCommandError, command_name: str, commands: dict = None
) -> None:
    """
    Handle command execution errors by displaying the error message and command help.

    Args:
        error: The command error
        command_name: The name of the command
        commands: Dictionary of available commands
    """
    print(f"Command Error: {str(error)}")
    if commands and command_name in commands:
        print(f"{Help.cmd(command_name, commands[command_name])}\n")
    else:
        print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")


def handle_generic_error(
    error: AppletError, command_name: str, commands: dict = None
) -> None:
    """
    Handle generic applet errors by displaying the error message and command help.

    Args:
        error: The general error
        command_name: The name of the command
        commands: Dictionary of available commands
    """
    print(f"Error: {str(error)}")
    if commands and command_name in commands:
        print(f"{Help.cmd(command_name, commands[command_name])}\n")
    else:
        print(f"{Fore.YELLOW}Command {command_name} not found{Style.RESET_ALL}")


def handle_applet_error(
    error: AppletError, command_name: str, commands: dict = None
) -> None:
    """
    Main error handler function that dispatches to specific handlers based on error type.

    Args:
        error: The error to handle
        command_name: The name of the command
        commands: Dictionary of available commands
    """
    if isinstance(error, AppletHelpError):
        handle_help_request(
            None, command_name, commands.get(command_name) if commands else None
        )
    elif isinstance(error, AppletValidationError):
        handle_validation_error(error, command_name, commands)
    elif isinstance(error, AppletNotFoundError):
        handle_not_found_error(error, command_name, commands)
    elif isinstance(error, AppletParseError):
        handle_parse_error(error, command_name, commands)
    elif isinstance(error, AppletCommandError):
        handle_command_error(error, command_name, commands)
    else:
        handle_generic_error(error, command_name, commands)
