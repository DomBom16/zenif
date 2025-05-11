from textwrap import dedent
from shutil import get_terminal_size as tsize
from typing import Any
from colorama import Fore, Back, Style
from .parameters import Parameter


class Help:
    @staticmethod
    def cli(cli_name: str, commands: dict[str, Any]) -> str:
        """
        Format help text for the entire CLI application in a visually pleasing style.
        Commands with aliases will display like "fetch, f".
        """
        lines = []
        lines.append(
            f"{Back.BLUE}{Fore.BLACK}  {cli_name} <command> [args]  {Style.RESET_ALL}"
        )
        lines.append("")

        lines.append(
            f"{Back.BLUE}{Fore.BLACK}  {'Command':<20} {'Description'.ljust(tsize().columns - 23)}{Style.RESET_ALL}"
        )

        # Format each primary command. If the command has aliases (stored on _aliases), list them.
        for name, command in sorted(commands.items()):
            # Get the aliases that were registered on the command.
            aliases = getattr(command, "_aliases", [])
            if aliases:
                # Build a display string like "fetch, f, another_alias"
                display_name = f"{name}, {', '.join(aliases)}"
            else:
                display_name = name

            doc = (
                command.__doc__.strip()
                if command.__doc__
                else "No description available."
            )
            first_line = doc.split("\n")[0]
            lines.append(
                f"{Fore.BLUE}  {display_name:<20} {first_line}{Style.RESET_ALL}"
            )
        return "\n".join(lines)

    @staticmethod
    def cmd(command_name: str, command: Any) -> str:
        """
        Format help text for a single command.
        If the command has aliases, list them next to the command name.
        """
        lines = []
        # Retrieve aliases registered on the command (if any)
        aliases = getattr(command, "_aliases", [])
        if aliases:
            header = (
                f"{Back.BLUE}{Fore.BLACK} {', '.join([command_name] + aliases)}"
                f"{Fore.BLUE}:{Style.RESET_ALL}{Fore.BLUE}  "
                f"{dedent(command.__doc__ if command.__doc__ else 'No description').strip().split('\n')[0]}"
                f"{Style.RESET_ALL}"
            )
        else:
            header = (
                f"{Back.BLUE}{Fore.BLACK} {command_name}{Fore.BLUE}:{Style.RESET_ALL}{Fore.BLUE}  "
                f"{dedent(command.__doc__ if command.__doc__ else 'No description').strip().split('\n')[0]}"
                f"{Style.RESET_ALL}"
            )
        lines.append(header)

        # Safely get the command documentation or a default message
        doc = command.__doc__ or "No description"
        doc_lines = dedent(doc).strip().split("\n")[1:]
        for line in doc_lines:
            lines.append(f"{Fore.BLUE}{Style.DIM}{line}{Style.RESET_ALL}")

        # Now, format the parameters (and their aliases, if set on the parameter objects).
        cli_params = getattr(command, "_cli_params", {})
        cli_aliases = getattr(command, "_cli_aliases", {})
        for param, alias in cli_aliases.items():
            if param in cli_params:
                if not alias.startswith("-"):
                    alias = f"-{alias}" if len(alias) == 1 else f"--{alias}"
                cli_params[param].alias = alias

        # Add a default help flag for the command.
        cli_params["--help"] = Parameter(
            param_name="help",
            kind="flag",
            help="Show this help menu",
            default=False,
            alias="h",
        )

        if cli_params:
            for param in sorted(cli_params.values(), key=lambda p: p.param_name):
                name = param.cli_name
                if name.startswith("--"):
                    name = "" + name
                elif name.startswith("-"):
                    name = " " + name
                else:
                    name = "  " + name
                if param.alias:
                    name += f" ({param.alias})"
                kind = param.kind.capitalize()
                default = param.default if param.default is not None else ""
                description = param.help
                lines.append("")
                lines.append(
                    f"{Fore.BLUE}{name}  {Style.DIM}{kind}\n{Fore.BLUE}{Style.DIM}  {description}{f"\n{Fore.RESET}  Defaults to {default}" if len(str(default)) > 0 and param.kind == "option" else ""}{Style.RESET_ALL}"
                )
        else:
            lines.append(
                f"{Fore.BLUE}No arguments defined for this command.{Style.RESET_ALL}"
            )

        return "\n".join(lines)
