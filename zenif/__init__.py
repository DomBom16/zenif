"""
zenif
~~~~~

Zenif is a powerful, highly customizable, and versatile Python module designed to enhance the efficiency and performance of your programs. Whether you're a seasoned developer or just starting out, Zenif offers a suite of tools to streamline your workflow and improve code management. Zenif currently enables developers with a simple yet highly customizable logger with support for multiple streams, a set of utility decorators, like @cache and @rate_limiter, and a handful of tools to create a command-line interface with interactive prompts and argument handling.
"""

# initialize colorama *once*
from colorama import init

from . import cli, decorators, log, schema

init(autoreset=True)

__version__ = "0.4.2"
__all__ = ["log", "decorators", "cli", "schema"]
