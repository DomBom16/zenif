from os import stat, chmod, path, unlink
from stat import S_IEXEC
from typing import Callable
from zenif.cli import CLI, kwarg
from zenif.log import Logger
from subprocess import run, CalledProcessError
from tempfile import NamedTemporaryFile

logger = Logger(ruleset={"log_line": {"format": "short"}})


def install_setup_command(cli: CLI, script_path: str) -> Callable:
    """
    Install a setup command for a Zenif CLI applet.

    This function creates a new command that generates a shell script to install
    the CLI applet as a Zsh command.

    Args:
        cli (CLI): The Zenif CLI instance to add the command to.
        script_path (str): The path to the main script of the CLI applet.

    Returns:
        Callable: The setup function that was added to the CLI.
    """

    @cli.command
    @kwarg("--alias", default=cli.name, help="Alias for the command")
    def setup(alias: str):
        """Install this script as a Zsh command"""
        install_script_content = f"""#!/bin/zsh
if [[ -f ~/.zshrc ]]; then
    if ! grep -q "{alias}()" ~/.zshrc; then
        echo '\n{alias}() {{' >> ~/.zshrc
        echo '    python {script_path} "$@"' >> ~/.zshrc
        echo '}}' >> ~/.zshrc
        echo "Command \033[44m\033[30m {alias} \033[0m has been added to your .zshrc file."
        echo "Run the following to get started:\n \nsource ~/.zshrc\n{alias} -h"
    else
        echo "The command \033[44m\033[30m {alias} \033[0m is already in your .zshrc file."
    fi
else
    echo "Error: ~/.zshrc file not found."
fi

# Delete this script
rm -f "$0"
"""

        with NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as temp_script:
            temp_script.write(install_script_content)
            temp_script_path = temp_script.name

        # Make the script executable
        st = stat(temp_script_path)
        chmod(temp_script_path, st.st_mode | S_IEXEC)

        logger.info(f"Executing installation script for '{alias}' command...")

        try:
            # Execute the script
            result = run(
                ["zsh", temp_script_path], check=True, text=True, capture_output=True
            )
            logger.success(result.stdout)
            if result.stderr:
                logger.warning(result.stderr)
        except CalledProcessError as e:
            logger.error(f"Installation failed with error: {e}")
            logger.error(e.stderr)
        finally:
            try:
                if "temp_script_path" in locals() and path.exists(temp_script_path):
                    unlink(temp_script_path)
                    logger.info("Installation script has been cleaned up.")
                else:
                    logger.info("No temporary script to clean up; already cleaned up.")
            except Exception as e:
                logger.warning(f"Failed to delete temporary script: {e}")

    return setup
