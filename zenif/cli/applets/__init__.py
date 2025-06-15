from .commands import (
    handle_help_flags,
    invoke_command,
    resolve_command,
    run_after_hook,
    run_before_hook,
    run_command,
    set_terminal_title,
)
from .core import Applet
from .error_handlers import (
    handle_applet_error,
    handle_command_error,
    handle_generic_error,
    handle_help_request,
    handle_not_found_error,
    handle_parse_error,
    handle_validation_error,
)
from .exceptions import (
    AppletCommandError,
    AppletConfigError,
    AppletError,
    AppletHelpError,
    AppletNotFoundError,
    AppletParseError,
    AppletValidationError,
)
from .parser import parse

__all__ = [
    # Core functionality
    "Applet",
    "parse",
    # Exception types
    "AppletError",
    "AppletParseError",
    "AppletCommandError",
    "AppletHelpError",
    "AppletConfigError",
    "AppletNotFoundError",
    "AppletValidationError",
    # Error handlers
    "handle_help_request",
    "handle_validation_error",
    "handle_not_found_error",
    "handle_parse_error",
    "handle_command_error",
    "handle_generic_error",
    "handle_applet_error",
    # Command runners
    "set_terminal_title",
    "run_before_hook",
    "run_after_hook",
    "handle_help_flags",
    "invoke_command",
    "run_command",
    "resolve_command",
]
