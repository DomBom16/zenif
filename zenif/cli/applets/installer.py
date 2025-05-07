import os
import stat
from pathlib import Path
from typing import Callable, TYPE_CHECKING
from ..prompt import Prompt
from ...log import Logger
from colorama import Fore, Back, Style

if TYPE_CHECKING:
    from .core import Applet


L = Logger({"log_line": {"format": [{"type": "static", "value": "  "}]}})


def friendly_path(path: Path) -> str:
    """
    Returns a string representation of a path with the home directory replaced by '~'
    if applicable.
    """
    home = str(Path.home())
    path_str = str(path)
    if path_str.startswith(home):
        return "" + path_str[len(home) :]
    return path_str


def detect_install_dir() -> Path:
    """
    Determine the target installation directory.
    If the process is run as root, use '/usr/local/bin';
    otherwise, prefer a user-writable directory such as '~/.local/bin' or '~/bin'.
    """
    if os.geteuid() == 0:  # Running as root
        return Path("/usr/local/bin")

    possible_dirs = [
        Path(os.environ.get("HOME", "")) / ".local" / "bin",
        Path(os.environ.get("HOME", "")) / "bin",
    ]
    for directory in possible_dirs:
        if directory.exists() and os.access(directory, os.W_OK):
            return directory
    # If none exist, attempt to create the first one:
    target = possible_dirs[0]
    target.mkdir(parents=True, exist_ok=True)
    return target


def ensure_shebang(script_path: Path) -> Path:
    """
    Ensure the target CLI script has a shebang line.
    If not, insert a shebang at the beginning of the file.
    Returns the path to the file with a proper shebang.
    """
    with open(script_path, "r+") as f:
        content = f.read()
        # Check if the first line is a shebang
        first_line = content.splitlines()[0] if content else ""
        if first_line.startswith("#!"):
            return script_path

        # Prepend the shebang to the content
        shebang = "#!/usr/bin/env python3\n"
        # Move the file pointer to the beginning to overwrite the file
        f.seek(0)
        f.write(shebang + content)
        f.truncate()  # In case the new content is shorter than the original

    # Ensure the script is executable
    st = os.stat(script_path)
    os.chmod(script_path, st.st_mode | stat.S_IEXEC)
    return script_path


def add_install_dir_to_zshrc(install_dir: Path) -> None:
    """
    Automatically add the installation directory to the user's PATH by updating ~/.zshrc.
    Uses a friendly display version for the installation directory.
    """
    home = Path.home()
    zshrc_path = home / ".zshrc"
    friendly_install_dir = friendly_path(install_dir)

    # Read the file if it exists.
    if zshrc_path.exists():
        content = zshrc_path.read_text()
        if str(install_dir) in content:
            L.info(
                f"{Fore.WHITE}{'Found'.ljust(15)}{Fore.YELLOW}{friendly_install_dir} {Fore.CYAN}>> {Fore.GREEN}{friendly_path(zshrc_path)}"
            )
            return
    else:
        L.info(
            f"{Fore.WHITE}{'Creating'.ljust(15)}{Fore.YELLOW}{friendly_path(zshrc_path)}"
        )

    export_line = f'\n# Added by Zenif CLI framework installer\nexport PATH="{install_dir}:$PATH"\n'

    L.info(
        f"{Fore.WHITE}{'Updating'.ljust(15)}{Fore.YELLOW}{friendly_path(zshrc_path)} {Fore.CYAN}>> {Fore.GREEN}{friendly_install_dir}"
    )
    with open(zshrc_path, "a") as f:
        f.write(export_line)
    L.success(
        f"{Fore.GREEN}{'Updated'.ljust(15)}{Fore.YELLOW}{friendly_path(zshrc_path)} {Fore.CYAN}>> {Fore.GREEN}{friendly_install_dir}"
    )


def install_setup(applet: "Applet", script_path: str) -> Callable:
    """
    Register an 'install' command that installs the CLI applet.
    This command creates a symbolic link in the target installation directory that points directly
    to the CLI script.
    """

    app = applet

    @app.command
    @app.opt("name", default=app.name.lower(), help="Name for the installed command")
    def install(name: str):
        """Install as a global command"""
        install_dir = detect_install_dir()
        original_script = Path(script_path)

        target_script = ensure_shebang(original_script)
        friendly_target_script = friendly_path(target_script)
        friendly_install_dir = friendly_path(install_dir)

        L.warning(
            f"{Fore.YELLOW}\033[1m\033[3mWARNING: install is not intended for production use, only use for development{Style.RESET_ALL}"
        )
        print()

        L.success(
            f"{Fore.GREEN}{'Started'.ljust(15)}{Fore.YELLOW}{target_script.name} {Fore.CYAN}>> {Fore.GREEN}{name}{Style.RESET_ALL}"
        )
        if original_script.is_symlink():
            L.info(
                f"{Fore.WHITE}{'Found'.ljust(15)}{Fore.YELLOW}{friendly_path(original_script)} {Fore.CYAN}>> {Fore.GREEN}{friendly_path(install_dir)}"
            )
            print()
            L.success(
                f"{Fore.GREEN}{'Completed'.ljust(15)}{Fore.YELLOW}{target_script.name} {Fore.CYAN}>> {Fore.GREEN}{name}{Style.RESET_ALL}"
            )
            print()
            L.success(
                f"{Fore.CYAN}Try running {Fore.BLACK}{Back.CYAN}  {name} --help  {Style.RESET_ALL}{Fore.CYAN} to get started{Style.RESET_ALL}"
            )
            return

        print()
        command_alias = (
            Prompt.text("Enter the command alias to install").default(name).ask()
        )
        print()
        L.success(
            f"{Fore.GREEN}{'Updated'.ljust(15)}{Fore.YELLOW}{target_script.name} {Fore.CYAN}>> {Fore.GREEN}{command_alias}{Style.RESET_ALL}"
        )
        print()
        confirm = (
            Prompt.confirm(
                f"Do you want to install {f'{app.name} as {command_alias}' if app.name != command_alias else app.name}?"
            )
            .default(False)
            .ask()
        )
        print()

        if not confirm:
            L.error(
                f"{Fore.RED}{'Aborted'.ljust(15)}{Fore.YELLOW}{target_script.name} {Fore.CYAN}>> {Fore.GREEN}{command_alias}{Style.RESET_ALL}"
            )
            return

        # Create a symlink in the install_dir.
        target_symlink = install_dir / command_alias
        friendly_target_symlink = friendly_path(target_symlink)
        L.info(
            f"{Fore.WHITE}{'Installing'.ljust(15)}{Fore.YELLOW}{friendly_target_script} {Style.DIM}({command_alias}){Style.RESET_ALL} {Fore.CYAN}>> {Fore.GREEN}{friendly_target_symlink}{Style.RESET_ALL}"
        )
        if target_symlink.exists() or target_symlink.is_symlink():
            L.warning(
                f"{Fore.YELLOW}{'Found'.ljust(15)}{Fore.YELLOW}{command_alias} {Fore.CYAN}>> {Fore.GREEN}{friendly_target_symlink}"
            )
            print()
            choice = Prompt.confirm("Overwrite existing command?").default(True).ask()
            print()
            if not choice:
                L.error(
                    f"{Fore.RED}{'Aborted'.ljust(15)}{Fore.YELLOW}{target_script.name} {Fore.CYAN}>> {Fore.GREEN}{command_alias}{Style.RESET_ALL}"
                )
                return
            try:
                L.info(
                    f"{Fore.WHITE}{'Removing'.ljust(15)}{Fore.YELLOW}{friendly_target_symlink}"
                )
                target_symlink.unlink()
                L.success(
                    f"{Fore.GREEN}{'Removed'.ljust(15)}{Fore.YELLOW}{friendly_target_symlink}"
                )
            except Exception as e:
                L.error(f"Could not remove existing command: {e}")
                return

        try:
            target_symlink.symlink_to(target_script)
            L.success(
                f"{Fore.GREEN}{'Installed'.ljust(15)}{Fore.YELLOW}{friendly_target_script} {Style.DIM}({command_alias}){Style.RESET_ALL} {Fore.CYAN}>> {Fore.GREEN}{friendly_target_symlink}{Style.RESET_ALL}"
            )
        except Exception as e:
            L.error(
                f"{Fore.RED}{'Failed'.ljust(15)}{Fore.YELLOW}installation {Fore.CYAN}>> {Fore.GREEN}{command_alias}{Style.RESET_ALL}: {Fore.RED}{e}{Style.RESET_ALL}"
            )
            return

        # Automatically add the installation directory to the user's PATH.
        L.info(
            f"{Fore.WHITE}{'Adding'.ljust(15)}{Fore.YELLOW}{friendly_install_dir}{Style.RESET_ALL} {Fore.CYAN}>> {Fore.GREEN}$PATH{Style.RESET_ALL}"
        )
        add_install_dir_to_zshrc(install_dir)
        L.success(
            f"{Fore.GREEN}{'Added'.ljust(15)}{Fore.YELLOW}{friendly_install_dir}{Style.RESET_ALL} {Fore.CYAN}>> {Fore.GREEN}$PATH{Style.RESET_ALL}"
        )
        print()
        L.success(
            f"{Fore.GREEN}{'Completed'.ljust(15)}{Fore.YELLOW}{target_script.name} {Fore.CYAN}>> {Fore.GREEN}{command_alias}{Style.RESET_ALL}"
        )
        print()
        L.success(
            f"{Fore.CYAN}Try running {Fore.BLACK}{Back.CYAN}  {command_alias} --help  {Style.RESET_ALL}{Fore.CYAN} to get started{Style.RESET_ALL}"
        )

    return install
