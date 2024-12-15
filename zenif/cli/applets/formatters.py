from textwrap import dedent


class HelpFormatter:
    @staticmethod
    def format_command_help(command_name: str, command: any) -> str:
        """Format help text for a single command."""
        help_text = [f"Command: {command_name}"]
        if command.__doc__:
            help_text.append(dedent(command.__doc__).strip())

        if hasattr(command, "_arguments"):
            help_text.append("\nArguments:")
            for args, kwargs in command._arguments:
                arg_help = f"  {', '.join(args)}"
                if "help" in kwargs:
                    arg_help += f": {kwargs['help']}"
                help_text.append(arg_help)

        return "\n".join(help_text)

    @staticmethod
    def format_cli_help(cli_name: str, commands: dict[str, any]) -> str:
        """Format help text for the entire CLI application."""
        help_text = [f"usage: {cli_name} <command> [args]", "\navailable commands:"]
        for name, command in commands.items():
            doc = command.__doc__.strip() if command.__doc__ else "no description"
            help_text.append(f"  {name}: {doc.split('\n')[0]}")
        return "\n".join(help_text)


class OutputFormatter:
    @staticmethod
    def format_output(output: any) -> str:
        """Format output for display."""
        if isinstance(output, (list, tuple)):
            return "\n".join(map(str, output))
        elif isinstance(output, dict):
            return "\n".join(f"{k}: {v}" for k, v in output.items())
        else:
            return str(output)
