from textwrap import dedent, indent
from shutil import get_terminal_size as tsize
from colorama import Fore, Back, Style


class HelpFormatter:
    @staticmethod
    def format_command_help(command_name: str, command: any) -> str:
        """
        Format help text for a single command in a visually pleasing manner.
        """
        lines = []
        lines.append(
            f"{Back.BLUE}{Fore.BLACK}  {command_name} {Fore.BLUE}│{Style.RESET_ALL}{Fore.BLUE}  {dedent(command.__doc__ if command.__doc__ else 'No description').strip().split('\n')[0]}{Style.RESET_ALL}"
        )

        if len(command.__doc__.split("\n")) > 1:

            def pred(s):
                return True

            doc = "\n".join(
                indent(
                    dedent(
                        "\n".join(command.__doc__.split("\n")[1:])
                        if command.__doc__
                        else "No description"
                    ),
                    " " * (len(command_name) + 3) + "│  ",
                    pred,
                )
                .strip()
                .split("\n")[1:]
            )
            lines.append(f"{Fore.BLUE}{Style.DIM}{doc}{Style.RESET_ALL}")
        lines.append("")

        cli_params = getattr(command, "_cli_params", {})
        cli_aliases = getattr(command, "_cli_aliases", {})
        for param, alias in cli_aliases.items():
            if param in cli_params:
                if not alias.startswith("-"):
                    alias = f"-{alias}" if len(alias) == 1 else f"--{alias}"
                cli_params[param].alias = alias
            else:
                pass

        if cli_params:
            header = (
                f"{Back.BLUE}{Fore.BLACK}{'  Parameter':<25} {'Type':<10} "
                f"{'Default':<10} {'Description'.ljust(tsize().columns - 48)}{Style.RESET_ALL}"
            )
            lines.append(header)

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
                lines.append(
                    f"{Fore.BLUE}{name:<25} {kind:<10} {str(default):<10} {description}{Style.RESET_ALL}"
                )
        else:
            lines.append(
                f"{Fore.BLUE}No arguments defined for this command.{Style.RESET_ALL}"
            )

        return "\n".join(lines)

    @staticmethod
    def format_cli_help(cli_name: str, commands: dict[str, any]) -> str:
        """
        Format help text for the entire CLI application in a visually pleasing style.
        """
        lines = []
        lines.append(
            f"{Back.BLUE}{Fore.BLACK}  {cli_name} <command> [args]  {Style.RESET_ALL}"
        )
        lines.append("")

        lines.append(
            f"{Back.BLUE}{Fore.BLACK}  {'Command':<20} {'Description'.ljust(tsize().columns - 23)}{Style.RESET_ALL}"
        )

        # Format each command with its first line of docstring (if available)
        for name, command in sorted(commands.items()):
            doc = (
                command.__doc__.strip()
                if command.__doc__
                else "No description available."
            )
            first_line = doc.split("\n")[0]
            lines.append(f"{Fore.BLUE}  {name:<20} {first_line}{Style.RESET_ALL}")
        return "\n".join(lines)
