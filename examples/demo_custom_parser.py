#!/usr/bin/env python3
"""
Demo script for the Zenif Applet custom parser.
This demonstrates different ways to pass arguments to Applet CLI tools.

Example usage:
- Basic root command:                   parser_demo
- Explicit root with args:              parser_demo root --branch feature-branch
- Root with direct args:                parser_demo --branch feature-branch
- Command with positional args:         parser_demo search /path/to/dir
- Command with alias:                   parser_demo find /path/to/dir
- Command with options:                 parser_demo search /path/to/dir --depth 3
- Command with equals format:           parser_demo search /path/to/dir --depth=3
- Command with short options:           parser_demo search /path/to/dir -d 3
- Command with joined numeric option:   parser_demo search /path/to/dir -d3
- Command with flag:                    parser_demo search /path/to/dir --quiet
- Command with short flags:             parser_demo search /path/to/dir -q
"""

import os
import sys

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zenif.cli.applets import Applet
from zenif.log import Logger

# Initialize logger
logger = Logger({"log_line": {"format": []}})

# Create applet
app = Applet()


@app.root
@app.opt("branch", default="main", help="Branch to operate on")
@app.flag("all", help="Show all branches")
def rootcmd(branch, all):
    """Root command that runs when no other command is specified"""
    if all:
        return f"Showing all branches with main branch: {branch}"
    return f"Operating on branch: {branch}"


@app.command(aliases=["find"])
@app.arg("path", help="Path to search")
@app.opt("depth", default=1, help="Search depth")
@app.opt("mode", default="normal", help="Search mode (normal, recursive, etc)")
@app.flag("quiet", help="Suppress output")
@app.alias("depth", "d")
@app.alias("quiet", "q")
@app.alias("mode", "m")
def search(path, depth, mode, quiet):
    """
    Search files in the given path.
    This command demonstrates different parameter types and formats.
    """
    if quiet:
        # Don't print anything in quiet mode
        return None

    return f"Searching in '{path}' with depth={depth}, mode={mode}"


@app.command
@app.arg("name", help="Project name")
@app.opt("template", default="default", help="Project template")
@app.flag("force", help="Overwrite existing project")
@app.alias("template", "t")
@app.alias("force", "f")
def create(name, template, force):
    """Create a new project with the given name and template"""
    if force:
        return (
            f"Creating project '{name}' with template '{template}' (forced overwrite)"
        )
    return f"Creating project '{name}' with template '{template}'"


@app.help
def show_help():
    """Custom help handler"""
    return "Demo application for Zenif Applet custom parser"


def main():
    try:
        app.run()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
