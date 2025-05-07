import re
from typing import Any, Callable, Dict, List, Tuple

from .exceptions import AppletError
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


class CustomCommandParser:
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
        self._organize_parameters()

    def _organize_parameters(self) -> None:
        """Organize parameters by type and build lookup maps."""
        # Get cli parameters; default to an empty dict if not defined
        cli_params = getattr(self.command, "_cli_params", {})
        cli_aliases = getattr(self.command, "_cli_aliases", {})

        # Apply aliases to parameters
        for param_name, alias in cli_aliases.items():
            if param_name in cli_params:
                cli_params[param_name].alias = alias

        # Organize parameters by type
        for name, param in cli_params.items():
            self.param_by_name[name] = param

            if param.kind == "argument":
                self.positional_params[name] = param
            elif param.kind == "option":
                self.option_params[name] = param
            elif param.kind == "flag":
                self.flag_params[name] = param

            # Register short aliases for quick lookup
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

    def parse_args(self, args: List[str]) -> Dict[str, Any]:
        """
        Parse the given command line arguments according to the command's parameters.

        Returns a dictionary with parameter names mapped to their values.

        Note: help flags (-h, --help) should be detected before calling this method.
        """
        result = {}
        positional_index = 0
        positional_args = list(self.positional_params.values())

        # Initialize default values
        for name, param in self.param_by_name.items():
            if param.default is not None:
                result[param.param_name] = param.default

        # Initialize flags as False
        for name in self.flag_params:
            result[name] = False

        # Check for help flag in arguments (as a fallback)
        if any(arg in HELP_FLAGS for arg in args):
            raise AppletError("Help requested")

        i = 0
        while i < len(args):
            arg = args[i]

            # Handle --option=value format
            if "=" in arg and arg.startswith("-"):
                option_name, value = arg.split("=", 1)
                if option_name.startswith("--"):
                    # Long option
                    param_name = option_name[2:]
                    if param_name in self.option_params:
                        result[param_name] = value
                    else:
                        raise AppletError(f"Unknown option: {option_name}")
                elif option_name.startswith("-"):
                    # Short option
                    short_name = option_name[1:]
                    param_name = self._resolve_short_option(short_name)
                    if param_name:
                        result[param_name] = value
                    else:
                        raise AppletError(
                            f"Unknown or ambiguous short option: {option_name}"
                        )
                i += 1
                continue

            # Handle -m10 format (joined short option with numeric value)
            if arg.startswith("-") and len(arg) > 2 and not arg.startswith("--"):
                short_opt, value = _split_joined_opt(arg)
                if value and _is_numeric(value):
                    param_name = self._resolve_short_option(short_opt)
                    if param_name:
                        result[param_name] = value
                        i += 1
                        continue

            # Handle --option value format or -o value format
            if arg.startswith("--"):
                # Check for help flag
                if arg == "--help":
                    raise AppletError("Help requested")

                option_name = arg[2:]
                if option_name in self.option_params:
                    if i + 1 < len(args) and not args[i + 1].startswith("-"):
                        result[option_name] = args[i + 1]
                        i += 2
                    else:
                        raise AppletError(f"Option {arg} requires a value")
                elif option_name in self.flag_params:
                    result[option_name] = True
                    i += 1
                else:
                    raise AppletError(f"Unknown option or flag: {arg}")
            elif arg.startswith("-"):
                short_name = arg[1:]

                # First check if it's an alias in our short_aliases dictionary
                # Check for help flag
                if arg in HELP_FLAGS:
                    raise AppletError("Help requested")

                # If it's an alias in our short_aliases dictionary
                if short_name in self.short_aliases:
                    param_name = self.short_aliases[short_name]
                    # Check if it's a flag or an option
                    if param_name in self.flag_params:
                        result[param_name] = True
                        i += 1
                    elif param_name in self.option_params:
                        if i + 1 < len(args) and not args[i + 1].startswith("-"):
                            result[param_name] = args[i + 1]
                            i += 2
                        else:
                            raise AppletError(f"Option {arg} requires a value")
                    continue

                # If not a direct alias, try to resolve
                option_param_name = self._resolve_short_option(short_name)
                flag_param_name = self._resolve_short_flag(short_name)

                # If it's an option
                if option_param_name:
                    if i + 1 < len(args) and not args[i + 1].startswith("-"):
                        result[option_param_name] = args[i + 1]
                        i += 2
                    else:
                        raise AppletError(f"Option {arg} requires a value")
                # If it's a flag
                elif flag_param_name:
                    result[flag_param_name] = True
                    i += 1
                else:
                    raise AppletError(
                        f"Unknown or ambiguous short option or flag: {arg}"
                    )
            else:
                # Positional argument
                if positional_index < len(positional_args):
                    param = positional_args[positional_index]
                    result[param.param_name] = arg
                    positional_index += 1
                    i += 1
                else:
                    raise AppletError(f"Too many positional arguments: {arg}")

        # Check if all required positional arguments were provided
        if positional_index < len(positional_args):
            missing_args = [p.param_name for p in positional_args[positional_index:]]
            raise AppletError(
                f"Missing required positional arguments: {', '.join(missing_args)}"
            )

        return result


def parse_command_args(command: Callable, args: List[str]) -> Dict[str, Any]:
    """
    Parse command arguments using the custom parser.
    Returns a dictionary mapping parameter names to their values.

    If help is requested (using -h or --help), raises AppletError
    to trigger help display in the calling code.
    """
    # First check if help flag is present anywhere in args
    if any(arg in HELP_FLAGS for arg in args):
        raise AppletError("Help requested")

    parser = CustomCommandParser(command)
    try:
        return parser.parse_args(args)
    except AppletError as e:
        # Re-raise the error to be caught by higher-level handlers
        raise e
