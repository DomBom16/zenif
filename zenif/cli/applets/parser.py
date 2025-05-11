import re
from typing import Any, Callable, Dict, List, Tuple

from .exceptions import (
    AppletError,
    AppletHelpError,
    AppletNotFoundError,
    AppletValidationError,
)
from .parameters import Parameter

# Define help flags for quick reference
HELP_FLAGS = ["-h", "--help"]


def _is_numeric(s: str) -> bool:
    """Check if a string contains only digits and is a valid number."""
    return bool(re.match(r"^-?\d+(\.\d+)?$", s))


def _split_joined_opt(arg: str) -> Tuple[str, str]:
    """Split an argument like -m10 into ('-m', '10')."""
    match = re.match(r"^(-[a-zA-Z])(\d+.*)$", arg)
    if match:
        return match.group(1), match.group(2)
    return arg, ""


def _is_help_requested(args: List[str]) -> bool:
    """Check if help was requested in the arguments."""
    return any(arg in HELP_FLAGS for arg in args)


def _is_potential_option(arg: str) -> bool:
    """Check if an argument is potentially an option (starts with a dash)."""
    return arg.startswith("-")


def _is_key_value_format(arg: str) -> bool:
    """Check if an argument is in key=value format."""
    return "=" in arg and arg.startswith("-")


class CommandParser:
    """
    A custom command parser for the Applet framework that supports various argument formats:
    - Positional arguments: cli path
    - Options with values: --mode maximum, -m maximum, --mode=maximum, -m=maximum, -m10
    - Flags: --all, -a
    """

    def __init__(self, command: Callable):
        self.command = command
        self.positional_params: Dict[str, Parameter] = {}
        self.option_params: Dict[str, Parameter] = {}
        self.flag_params: Dict[str, Parameter] = {}
        self.param_by_name: Dict[str, Parameter] = {}
        self.short_aliases: Dict[
            str, str
        ] = {}  # Maps single-letter aliases to param names
        self.cli_params = {}
        self.cli_aliases = {}
        self._organize_parameters()

    def _organize_parameters(self) -> None:
        """Organize parameters by type and build lookup maps."""
        self._load_param_definitions()
        self._apply_param_aliases()
        self._categorize_params_by_type()
        self._register_short_aliases()

    def _load_param_definitions(self) -> None:
        """Load parameter definitions from the command."""
        # Get cli parameters; default to an empty dict if not defined
        self.cli_params = getattr(self.command, "_cli_params", {})
        self.cli_aliases = getattr(self.command, "_cli_aliases", {})

    def _apply_param_aliases(self) -> None:
        """Apply aliases to parameters."""
        for param_name, alias in self.cli_aliases.items():
            if param_name in self.cli_params:
                self.cli_params[param_name].alias = alias

    def _categorize_params_by_type(self) -> None:
        """Categorize parameters by their type."""
        for name, param in self.cli_params.items():
            self.param_by_name[name] = param

            if param.kind == "argument":
                self.positional_params[name] = param
            elif param.kind == "option":
                self.option_params[name] = param
            elif param.kind == "flag":
                self.flag_params[name] = param

    def _register_short_aliases(self) -> None:
        """Register short aliases for quick lookup."""
        for name, param in self.param_by_name.items():
            if param.alias:
                alias_key = param.alias.strip("-")
                if len(alias_key) == 1:
                    self.short_aliases[alias_key] = name

    def _resolve_short_option(self, short_opt: str) -> str:
        """
        Resolve a short option like -m to its full parameter name.
        Return None if no match or multiple matches.
        """
        letter = short_opt.strip("-")

        # Check explicit aliases first
        if letter in self.short_aliases:
            return self.short_aliases[letter]

        # Otherwise, find parameters that start with this letter
        matching_params = []
        for name in self.option_params:
            if name.startswith(letter):
                matching_params.append(name)

        # Return the parameter name if exactly one match, otherwise None
        if len(matching_params) == 1:
            return matching_params[0]
        return None

    def _resolve_short_flag(self, short_flag: str) -> str:
        """
        Resolve a short flag like -v to its full parameter name.
        Return None if no match or multiple matches.
        """
        letter = short_flag.strip("-")

        # Check explicit aliases first
        if letter in self.short_aliases:
            return self.short_aliases[letter]

        # Otherwise, find flags that start with this letter
        matching_flags = []
        for name in self.flag_params:
            if name.startswith(letter):
                matching_flags.append(name)

        # Return the flag name if exactly one match, otherwise None
        if len(matching_flags) == 1:
            return matching_flags[0]
        return None

    def _initialize_param_values(self) -> Dict[str, Any]:
        """Initialize parameter values with defaults."""
        result = {}

        # Initialize default values for options
        for name, param in self.param_by_name.items():
            if param.default is not None:
                result[param.param_name] = param.default

        # Initialize flags as False
        for name in self.flag_params:
            result[name] = False

        return result

    def _handle_key_value_arg(self, arg: str, result: Dict[str, Any], i: int) -> int:
        """Handle arguments in key=value format."""
        option_name, value = arg.split("=", 1)
        if option_name.startswith("--"):
            # Long option
            param_name = option_name[2:]
            if param_name in self.option_params:
                result[param_name] = value
            else:
                raise AppletNotFoundError(f"Unknown option: {option_name}")
        elif option_name.startswith("-"):
            # Short option
            short_name = option_name[1:]
            param_name = self._resolve_short_option(short_name)
            if param_name:
                result[param_name] = value
            else:
                raise AppletNotFoundError(
                    f"Unknown or ambiguous short option: {option_name}"
                )
        return i + 1

    def _is_joined_numeric_option(self, arg: str) -> bool:
        """Check if argument is a joined numeric option like -m10."""
        return arg.startswith("-") and len(arg) > 2 and not arg.startswith("--")

    def _handle_joined_numeric_option(
        self, arg: str, result: Dict[str, Any], i: int
    ) -> int:
        """Handle arguments in -m10 format (joined short option with numeric value)."""
        short_opt, value = _split_joined_opt(arg)
        if value and _is_numeric(value):
            param_name = self._resolve_short_option(short_opt)
            if param_name:
                result[param_name] = value
                return i + 1
        return i  # If not handled, return the same index for normal processing

    def _handle_long_option(
        self, arg: str, args: List[str], result: Dict[str, Any], i: int
    ) -> int:
        """Handle long option arguments (--option)."""
        # Check for help flag
        if arg == "--help":
            raise AppletHelpError("Help requested")

        option_name = arg[2:]
        if option_name in self.option_params:
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                result[option_name] = args[i + 1]
                return i + 2
            else:
                raise AppletValidationError(f"Option {arg} requires a value")
        elif option_name in self.flag_params:
            result[option_name] = True
            return i + 1
        else:
            raise AppletNotFoundError(f"Unknown option or flag: {arg}")

    def _handle_short_option(
        self, arg: str, args: List[str], result: Dict[str, Any], i: int
    ) -> int:
        """Handle short option arguments (-o)."""
        short_name = arg[1:]

        # Check for help flag
        if arg in HELP_FLAGS:
            raise AppletHelpError("Help requested")

        # If it's a registered alias in our short_aliases dictionary
        if short_name in self.short_aliases:
            return self._handle_known_short_alias(short_name, arg, args, result, i)

        # If not a direct alias, try to resolve
        return self._handle_resolved_short_option(short_name, arg, args, result, i)

    def _handle_known_short_alias(
        self, short_name: str, arg: str, args: List[str], result: Dict[str, Any], i: int
    ) -> int:
        """Handle a short option that is a known alias."""
        param_name = self.short_aliases[short_name]
        # Check if it's a flag or an option
        if param_name in self.flag_params:
            result[param_name] = True
            return i + 1
        elif param_name in self.option_params:
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                result[param_name] = args[i + 1]
                return i + 2
            else:
                raise AppletValidationError(f"Option {arg} requires a value")
        return i + 1  # Default case

    def _handle_resolved_short_option(
        self, short_name: str, arg: str, args: List[str], result: Dict[str, Any], i: int
    ) -> int:
        """Handle a short option by resolving it to a parameter name."""
        option_param_name = self._resolve_short_option(short_name)
        flag_param_name = self._resolve_short_flag(short_name)

        # If it's an option
        if option_param_name:
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                result[option_param_name] = args[i + 1]
                return i + 2
            else:
                raise AppletValidationError(f"Option {arg} requires a value")
        # If it's a flag
        elif flag_param_name:
            result[flag_param_name] = True
            return i + 1
        else:
            raise AppletNotFoundError(
                f"Unknown or ambiguous short option or flag: {arg}"
            )

    def _handle_positional_arg(
        self,
        arg: str,
        positional_args: List[Parameter],
        result: Dict[str, Any],
        positional_index: int,
        i: int,
    ) -> int:
        """Handle a positional argument."""
        if positional_index < len(positional_args):
            param = positional_args[positional_index]
            result[param.param_name] = arg
            return i + 1
        else:
            raise AppletValidationError(f"Too many positional arguments: {arg}")

    def _validate_required_positional_args(
        self, positional_args: List[Parameter], positional_index: int
    ) -> None:
        """Validate that all required positional arguments were provided."""
        if positional_index < len(positional_args):
            missing_args = [p.param_name for p in positional_args[positional_index:]]
            raise AppletValidationError(
                f"Missing required positional arguments: {', '.join(missing_args)}"
            )

    def parse_args(self, args: List[str]) -> Dict[str, Any]:
        """
        Parse the given command line arguments according to the command's parameters.

        Returns a dictionary with parameter names mapped to their values.

        Note: help flags (-h, --help) should be detected before calling this method.
        """
        result = self._initialize_param_values()
        positional_index = 0
        positional_args = list(self.positional_params.values())

        # Check for help flag in arguments (as a fallback)
        if _is_help_requested(args):
            raise AppletHelpError("Help requested")

        i = 0
        while i < len(args):
            arg = args[i]

            # Handle --option=value format
            if _is_key_value_format(arg):
                i = self._handle_key_value_arg(arg, result, i)
                continue

            # Handle -m10 format (joined short option with numeric value)
            if self._is_joined_numeric_option(arg):
                i = self._handle_joined_numeric_option(arg, result, i)
                continue

            # Handle --option value format or -o value format
            if arg.startswith("--"):
                i = self._handle_long_option(arg, args, result, i)
            elif arg.startswith("-"):
                i = self._handle_short_option(arg, args, result, i)
            else:
                # Positional argument
                i = self._handle_positional_arg(
                    arg, positional_args, result, positional_index, i
                )
                positional_index += 1

        # Check if all required positional arguments were provided
        self._validate_required_positional_args(positional_args, positional_index)

        return result


def _check_for_help_request(args: List[str]) -> None:
    """Check if help is requested in the arguments."""
    if _is_help_requested(args):
        raise AppletHelpError("Help requested")


def _parse_with_command_parser(command: Callable, args: List[str]) -> Dict[str, Any]:
    """Parse arguments using the CommandParser."""
    parser = CommandParser(command)
    try:
        parsed_args = parser.parse_args(args)
        return parsed_args
    except AppletError as e:
        # Re-raise the error to be caught by higher-level handlers
        raise e


def parse(command: Callable, args: List[str]) -> Dict[str, Any]:
    """
    Parse command arguments using the custom parser.
    Returns a dictionary mapping parameter names to their values.

    If help is requested (using -h or --help), raises AppletHelpError
    to trigger help display in the calling code.
    """
    _check_for_help_request(args)
    return _parse_with_command_parser(command, args)
