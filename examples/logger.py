#!/usr/bin/env python3
"""
Comprehensive Zenif Logger Demo

This script demonstrates all the major features of the Zenif logging system,
including basic logging, stream management, custom formatting, and advanced usage.
"""

import os
import sys
from datetime import datetime

from zenif.log import Logger, StructuredLogger


def demo_basic_logging():
    """Demonstrate basic logging functions and features."""
    print("\n" + "=" * 60)
    print("BASIC LOGGING DEMO")
    print("=" * 60)

    # Initialize basic logger
    logger = Logger()

    # Test all logging levels
    logger.info("Application started successfully")
    logger.debug("Debug information for troubleshooting")
    logger.success("Operation completed successfully")
    logger.warning("This is a warning message")
    logger.error("An error occurred during processing")
    logger.lethal("Critical system failure detected")

    # Demonstrate multiple values and separator
    username = "alice"
    action = "login"
    timestamp = datetime.now()
    logger.info("User", username, "performed", action, "at", timestamp, sep=" | ")

    # Demonstrate rich formatting with complex data
    user_data = {
        "username": "bob",
        "roles": ["admin", "user"],
        "preferences": {"theme": "dark", "notifications": True},
        "last_login": "2024-01-15T10:30:00Z",
    }
    logger.info("User data with rich formatting:", user_data)


def demo_structured_logging():
    """Demonstrate StructuredLogger with keyword arguments."""
    print("\n" + "=" * 60)
    print("STRUCTURED LOGGING DEMO")
    print("=" * 60)

    slogger = StructuredLogger()

    # Log with structured data using kwargs
    slogger.info("User authentication", user="alice", ip="192.168.1.100", success=True)
    slogger.warning(
        "High CPU usage detected", cpu_percent=85.7, threshold=80, server="web-01"
    )
    slogger.error(
        "Database connection failed",
        host="db.example.com",
        port=5432,
        error_code="CONNECTION_TIMEOUT",
        retry_count=3,
    )


def demo_stream_management():
    """Demonstrate file streams and stream groups."""
    print("\n" + "=" * 60)
    print("STREAM MANAGEMENT DEMO")
    print("=" * 60)

    logger = Logger()

    # Create log directory if it doesn't exist
    log_dir = "zenif/logs"
    os.makedirs(log_dir, exist_ok=True)

    # Add individual file streams
    app_log = logger.stream.file.add(f"{log_dir}/application.log")
    error_log = logger.stream.file.add(f"{log_dir}/errors.log")
    debug_log = logger.stream.file.add(f"{log_dir}/debug.log")

    logger.info("Logging to multiple files simultaneously")
    logger.error("This error will appear in all log files")

    # Create a file group for easier management
    file_group = logger.fhgroup(app_log, error_log, debug_log)

    # Create console group
    console_group = logger.shgroup(
        logger.stream.normal.add(sys.stdout), logger.stream.normal.add(sys.stderr)
    )

    logger.success("Stream groups created successfully")

    # Demonstrate stream modification
    logger.stream.file.modify(
        error_log, ruleset={"timestamps": {"always_show": True, "use_utc": True}}
    )

    logger.info("Modified error log stream to always show UTC timestamps")

    return logger, file_group, console_group


def demo_custom_formatting():
    """Demonstrate custom log line formatting."""
    print("\n" + "=" * 60)
    print("CUSTOM FORMATTING DEMO")
    print("=" * 60)

    logger = Logger()

    # Test premade formats
    formats = ["default", "filled", "noalign", "simple", "short", "timestamp", "level"]

    for fmt in formats:
        logger.stream.normal.modify(
            sys.stdout,
            ruleset={"log_line": {"format": fmt}, "timestamps": {"always_show": True}},
        )
        logger.info(f"Using '{fmt}' format")

    # Reset to default
    logger.stream.normal.modify(
        sys.stdout,
        ruleset={
            "log_line": {"format": "default"},
            "timestamps": {"always_show": True},
        },
    )

    # Custom format definition
    custom_format = [
        {
            "type": "template",
            "value": "timestamp",
            "parameters": [
                {"color": {"foreground": "green"}},
                {"style": {"bold": True}},
            ],
        },
        {"type": "static", "value": " │ "},
        {
            "type": "template",
            "value": "level",
            "parameters": [
                {"case": "upper"},
                {"align": {"alignment": "center", "width": 8}},
                {"color": {"foreground": "yellow", "background": "blue"}},
                {"style": {"bold": True}},
            ],
        },
        {"type": "static", "value": " │ "},
        {
            "type": "template",
            "value": "filename",
            "parameters": [
                {"color": {"foreground": "magenta"}},
                {"truncate": {"width": 20, "position": "start"}},
                {"affix": {"prefix": "[", "suffix": "]"}},
            ],
        },
        {"type": "static", "value": ":"},
        {
            "type": "template",
            "value": "linenum",
            "parameters": [
                {"color": {"foreground": "cyan"}},
                {"style": {"italic": True}},
            ],
        },
        {"type": "static", "value": " │ "},
    ]

    logger.stream.normal.modify(
        sys.stdout, ruleset={"log_line": {"format": custom_format}}
    )
    logger.info("This uses a custom format with colors and styling")
    logger.warning("Custom format with different styling parameters")

    # Reset to default for subsequent demos
    logger.stream.normal.modify(
        sys.stdout,
        ruleset={
            "log_line": {"format": "default"},
            "timestamps": {"always_show": True},
        },
    )


def demo_advanced_features():
    """Demonstrate advanced logger features."""
    print("\n" + "=" * 60)
    print("ADVANCED FEATURES DEMO")
    print("=" * 60)

    logger = Logger()

    # Create log directory
    log_dir = "examples/example_logs"
    os.makedirs(log_dir, exist_ok=True)

    # Configure different streams with different rules
    detailed_log = logger.stream.file.add(f"{log_dir}/detailed.log")
    summary_log = logger.stream.file.add(f"{log_dir}/summary.log")

    # Detailed log with all information
    logger.stream.file.modify(
        detailed_log,
        ruleset={
            "timestamps": {"always_show": True, "use_utc": True},
            "log_line": {"format": "default"},
        },
    )

    # Summary log with minimal information
    logger.stream.file.modify(
        summary_log,
        ruleset={
            "timestamps": {"always_show": False},
            "log_line": {"format": "simple"},
        },
    )

    # Configure console with filled format
    logger.stream.normal.modify(sys.stdout, ruleset={"log_line": {"format": "filled"}})

    logger.info("This message appears differently in each stream")
    logger.error("Error messages are formatted consistently across streams")

    # Demonstrate conditional formatting based on terminal width
    responsive_format = [
        {
            "type": "template",
            "value": "timestamp",
            "parameters": [{"color": {"foreground": "green"}}],
        },
        {"type": "static", "value": " "},
        {
            "type": "template",
            "value": "level",
            "parameters": [
                {"case": "upper"},
                {"align": {"alignment": "left", "width": 7}},
                {"color": {"foreground": "yellow"}},
            ],
        },
        {"type": "static", "value": " "},
        {
            "type": "template",
            "value": "filename",
            "parameters": [
                {"color": {"foreground": "magenta"}},
                {
                    "if": {
                        "condition": {"type": "breakpoint", "value": {"min": 100}},
                        "action": {
                            "type": "parameters",
                            "value": [{"truncate": {"width": 30, "position": "start"}}],
                        },
                    }
                },
                {
                    "if": {
                        "condition": {"type": "breakpoint", "value": {"max": 100}},
                        "action": {
                            "type": "parameters",
                            "value": [
                                {"truncate": {"width": 15, "position": "middle"}}
                            ],
                        },
                    }
                },
            ],
        },
        {"type": "static", "value": " "},
    ]

    logger.stream.normal.modify(
        sys.stdout, ruleset={"log_line": {"format": responsive_format}}
    )
    logger.info("This format adapts to terminal width")
    logger.debug("Resize your terminal to see the filename truncation change")


def demo_template_parameters():
    """Demonstrate various template parameters."""
    print("\n" + "=" * 60)
    print("TEMPLATE PARAMETERS DEMO")
    print("=" * 60)

    logger = Logger()

    # Demonstrate masking for sensitive data
    masked_format = [
        {
            "type": "template",
            "value": "timestamp",
            "parameters": [{"color": {"foreground": "green"}}],
        },
        {"type": "static", "value": " "},
        {"type": "template", "value": "level", "parameters": [{"case": "upper"}]},
        {"type": "static", "value": " "},
        {
            "type": "static",
            "value": "API_KEY_12345678",
            "parameters": [
                {"mask": {"width": (13, 4), "masker": "*", "position": "middle"}},
                {"color": {"foreground": "red"}},
            ],
        },
        {"type": "static", "value": " "},
    ]

    logger.stream.normal.modify(
        sys.stdout, ruleset={"log_line": {"format": masked_format}}
    )
    logger.info("Sensitive data is masked in logs")

    # Demonstrate filtering
    filter_format = [
        {
            "type": "template",
            "value": "timestamp",
            "parameters": [{"color": {"foreground": "green"}}],
        },
        {"type": "static", "value": " "},
        {
            "type": "template",
            "value": "level",
            "parameters": [
                {"case": "upper"},
                {"filter": {"mode": "exclude", "items": ["INFO"], "replace": "EVENT"}},
                {"color": {"foreground": "cyan"}},
            ],
        },
        {"type": "static", "value": " "},
    ]

    logger.stream.normal.modify(
        sys.stdout, ruleset={"log_line": {"format": filter_format}}
    )
    logger.info("INFO level is replaced with EVENT")
    logger.warning("WARNING level remains unchanged")

    # Reset to default
    logger.stream.normal.modify(sys.stdout, ruleset={"log_line": {"format": "default"}})


def demo_error_handling():
    """Demonstrate error handling and logging patterns."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING DEMO")
    print("=" * 60)

    logger = Logger()
    slogger = StructuredLogger()

    # Simulate various error scenarios
    try:
        # Simulate a division by zero error
        result = 10 / 0
        print(result)
    except ZeroDivisionError as e:
        logger.error("Division by zero error occurred", str(e))
        slogger.error(
            "Mathematical error",
            operation="division",
            dividend=10,
            divisor=0,
            error=str(e),
        )

    try:
        # Simulate a file not found error
        with open("nonexistent_file.txt", "r") as f:
            content = f.read()
            print(content)
    except FileNotFoundError as e:
        logger.error("File not found", str(e))
        slogger.error(
            "File operation failed",
            operation="read",
            filename="nonexistent_file.txt",
            error=str(e),
        )

    # Log successful operations
    logger.success("Error handling demo completed successfully")


def cleanup_demo_files():
    """Clean up demo log files."""
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)

    log_dir = "examples/example_logs"
    if os.path.exists(log_dir):
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except OSError as e:
                print(f"Error removing {file_path}: {e}")

        try:
            os.rmdir(log_dir)
            print(f"Removed directory: {log_dir}")
        except OSError as e:
            print(f"Error removing directory {log_dir}: {e}")

    print("Cleanup completed")


def main():
    """Run all logger demos."""
    print("ZENIF LOGGER COMPREHENSIVE DEMO")
    print("=" * 60)
    print("This demo showcases all major features of the Zenif Logger system.")
    print("Each section demonstrates different capabilities and use cases.")

    try:
        # Run all demo sections
        demo_basic_logging()
        demo_structured_logging()
        demo_stream_management()
        demo_custom_formatting()
        demo_template_parameters()
        demo_advanced_features()
        demo_error_handling()

        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("All features have been demonstrated.")
        print("Check the generated log files in the 'zenif/logs' directory.")

    except Exception as e:
        logger = Logger()
        logger.lethal(f"Demo failed with error: {e}")
        raise

    # finally:
    #     # Clean up demo files
    #     cleanup_demo_files()


if __name__ == "__main__":
    main()
