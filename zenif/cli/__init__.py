from .applets.core import CLI
from .applets.decorators import arg, kwarg
from .applets.install_command import install_setup_command

from .prompt import Prompt


__all__ = [
    # CLI()
    "CLI",
    # CLI().command decorators
    "arg",
    "kwarg",
    # setup command installer
    "install_setup_command",
    # interactive prompt utils
    "Prompt",
]
