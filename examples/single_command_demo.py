#!/usr/bin/env python3
"""
Demo script for the Zenif Applet's single command mode.

This script demonstrates how to create a CLI tool that works as a single command
without needing to specify subcommands.

Example usage:
- Basic command: ./single_command_demo.py ./path/to/file
- With options: ./single_command_demo.py ./path/to/file --output result.txt
- With flags: ./single_command_demo.py ./path/to/file -v
- With short options: ./single_command_demo.py ./path/to/file -o result.txt
- With numeric options: ./single_command_demo.py ./path/to/file -l5
- With help flag: ./single_command_demo.py -h
"""

import os
import sys

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zenif.cli.applets import Applet
from zenif.log import Logger

# Initialize logger
logger = Logger({"log_line": {"format": []}})

# Create applet in single command mode
app = Applet(single=True)


@app.single
@app.arg("file", help="Input file to process")
@app.opt("output", default="output.txt", help="Output file name")
@app.opt("limit", default=10, help="Limit the number of lines processed")
@app.flag("verbose", help="Enable verbose output")
@app.flag("overwrite", help="Overwrite existing output file")
@app.alias("output", "o")
@app.alias("limit", "l")
@app.alias("verbose", "v")
def process(file, output, limit, verbose, overwrite):
    """
    Process the input file and write results to the output file.

    This demonstrates using the Applet framework in single command mode,
    where you don't need to specify a subcommand.
    """
    if verbose:
        logger.info(f"Processing file: {file}")
        logger.info(f"Output file: {output}")
        logger.info(f"Line limit: {limit}")
        logger.info(f"Overwrite mode: {overwrite}")

    # Check if file exists
    if not os.path.exists(file):
        return f"Error: File '{file}' does not exist"

    # Check if output file exists and overwrite flag is not set
    if os.path.exists(output) and not overwrite:
        return f"Error: Output file '{output}' already exists. Use --overwrite to replace it."

    try:
        # Read input file (up to limit)
        with open(file, "r") as f:
            lines = f.readlines()[: int(limit)]

        # Process lines (in this demo, we just uppercase them)
        processed_lines = [line.upper() for line in lines]

        # Write to output file
        with open(output, "w") as f:
            f.writelines(processed_lines)

        if verbose:
            logger.success(f"Successfully processed {len(processed_lines)} lines")

        return f"Processed {len(processed_lines)} lines from '{file}' and saved to '{output}'"

    except Exception as e:
        return f"Error processing file: {str(e)}"


def main():
    try:
        app.run()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
