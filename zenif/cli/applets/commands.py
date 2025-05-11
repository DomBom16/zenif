from typing import Any, Callable, Dict, List, Optional

from ...log import Logger
from .error_handlers import handle_applet_error, handle_help_request
from .exceptions import AppletError, AppletHelpError
from .parser import HELP_FLAGS, parse

L = Logger({"log_line": {"format": []}})


def set_terminal_title(
    applet_name: str, command_name: str, args: List[str] = None
) -> None:
    """
    Set the terminal title to reflect the currently running command.

    Args:
        applet_name: The name of the applet
        command_name: The name of the command being executed
        args: Command arguments
    """
    if args:
        print(f"\x1b]2;{applet_name} {command_name} {' '.join(args)}\x07", end="")
    else:
        print(f"\x1b]2;{applet_name} {command_name}\x07", end="")


def execute_before_callback(
    before_callback: Callable, command_name: str, args: List[str]
) -> None:
    """
    Execute the before callback for a command if one is defined.

    Args:
        before_callback: The callback to execute before running a command
        command_name: The name of the command to be executed
        args: Command arguments
    """
    if before_callback:
        result = before_callback(command_name, args)
        if result is not None:
            L.info(result)


def execute_after_callback(
    after_callback: Callable, command_name: str, args: List[str]
) -> None:
    """
    Execute the after callback for a command if one is defined.

    Args:
        after_callback: The callback to execute after running a command
        command_name: The name of the command that was executed
        args: Command arguments
    """
    if after_callback:
        result = after_callback(command_name, args)
        if result is not None:
            L.info(result)


def check_for_help_flags(
    args: List[str],
    help_callback: Optional[Callable],
    command_name: str,
    command: Callable,
) -> bool:
    """
    Check if help flags are present in the arguments and handle them if found.

    Args:
        args: Command arguments to check
        help_callback: Optional callback function for help requests
        command_name: The name of the command
        command: The command function

    Returns:
        True if help flags were found and handled, False otherwise
    """
    if any(arg in HELP_FLAGS for arg in args):
        handle_help_request(help_callback, command_name, command)
        return True
    return False


def run_command(
    command: Callable,
    args: List[str],
    applet_name: str = None,
    command_name: str = None,
) -> Any:
    """
    Parse arguments and run a command with error handling.

    Args:
        command: The command function to execute
        args: Command arguments
        applet_name: Optional applet name for terminal title
        command_name: Optional command name for terminal title and error handling

    Returns:
        The result of the command execution
    """
    try:
        parsed_args = parse(command, args)

        # Set terminal title if applet_name is provided
        if applet_name and command_name:
            set_terminal_title(applet_name, command_name, args)

        # Execute the command with parsed arguments
        result = command(**parsed_args)

        # Return the result (will be logged by caller if not None)
        return result
    except AppletError as e:
        # Pass the exception up to be handled by the caller
        raise e


def execute_command(
    command: Callable,
    args: List[str],
    applet_name: str,
    command_name: str,
    help_callback: Optional[Callable] = None,
    before_callback: Optional[Callable] = None,
    after_callback: Optional[Callable] = None,
    commands: Dict[str, Callable] = None,
) -> Any:
    """
    Execute a command with full error handling and callbacks.

    Args:
        command: The command function to execute
        args: Command arguments
        applet_name: The name of the applet for terminal title
        command_name: The name of the command for terminal title and error handling
        help_callback: Optional callback function for help requests
        before_callback: Optional callback to run before the command
        after_callback: Optional callback to run after the command
        commands: Dictionary of available commands for error handling

    Returns:
        The result of the command execution, or None if an error occurred
    """
    # Check for help flags first
    if check_for_help_flags(args, help_callback, command_name, command):
        return None

    # Execute before callback if defined
    if before_callback:
        execute_before_callback(before_callback, command_name, args)

    try:
        # Run the command and get the result
        result = run_command(command, args, applet_name, command_name)

        # Log the result if it's not None
        if result is not None:
            L.info(result)

        return result
    except AppletHelpError:
        handle_help_request(help_callback, command_name, command)
    except AppletError as e:
        handle_applet_error(e, command_name, commands)
    finally:
        # Execute after callback if defined
        if after_callback:
            execute_after_callback(after_callback, command_name, args)

    return None


def resolve_command(
    command_name: str, commands: Dict[str, Callable], aliases: Dict[str, str]
) -> str:
    """
    Resolve a command name to its primary name, considering aliases.

    Args:
        command_name: The name of the command to resolve
        commands: Dictionary of available commands
        aliases: Dictionary mapping aliases to primary command names

    Returns:
        The resolved command name, or the original if not found
    """
    if command_name in commands:
        return command_name
    elif command_name in aliases:
        return aliases[command_name]
    return command_name
