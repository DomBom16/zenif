# FluxUtils

FluxUtils is a powerful, highly customizable, and versatile Python module designed to enhance the efficiency and performance of your programs. Whether you're a seasoned developer or just starting out, FluxUtils offers a suite of tools to streamline your workflow and improve code management. FluxUtils currently enables developers with a simple yet highly customizable logger with support for multiple streams, a set of utility decorators, like `@cache` and `@rate_limiter`, and a handful of tools to create a command-line interface with interactive prompts and argument handling.

## Table of Contents

- [FluxUtils](#fluxutils)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Log Module](#log-module)
    - [Initialization](#initialization)
    - [Logging Functions](#logging-functions)
      - [`*values`](#values)
      - [`sep`](#sep)
      - [`rich`](#rich)
    - [Streams and File Handling](#streams-and-file-handling)
      - [Adding and Removing Streams](#adding-and-removing-streams)
      - [Stream Groups](#stream-groups)
      - [Modifying Stream Behavior](#modifying-stream-behavior)
      - [Resetting Streams](#resetting-streams)
    - [Rules and Customization](#rules-and-customization)
      - [Accessing and Modifying Rules](#accessing-and-modifying-rules)
      - [Viewing Rules](#viewing-rules)
      - [Rule Categories](#rule-categories)
    - [Customizing the Log Line](#customizing-the-log-line)
      - [Premade Formats](#premade-formats)
      - [Custom Format Definition](#custom-format-definition)
      - [Segment Types](#segment-types)
      - [Built-in Templates](#built-in-templates)
      - [Template Parameters](#template-parameters)
    - [Advanced Usage](#advanced-usage)
      - [Multiple Streams with Different Configurations](#multiple-streams-with-different-configurations)
      - [Dynamic Formatting Based on Terminal Size](#dynamic-formatting-based-on-terminal-size)
      - [Custom Logging Levels](#custom-logging-levels)
  - [Decorators Module](#decorators-module)
    - [retry](#retry)
    - [retry\_exponential\_backoff](#retry_exponential_backoff)
    - [timeout](#timeout)
    - [rate\_limiter](#rate_limiter)
    - [trace](#trace)
    - [suppress\_exceptions](#suppress_exceptions)
    - [deprecated](#deprecated)
    - [type\_check](#type_check)
    - [log\_execution\_time](#log_execution_time)
    - [cache](#cache)
    - [requires\_permission](#requires_permission)
  - [CLI Module](#cli-module)
    - [Basic Usage](#basic-usage)
      - [How It Works](#how-it-works)
      - [Running Your Application](#running-your-application)
      - [Key Points](#key-points)
    - [Interactive Prompts](#interactive-prompts)
    - [Available Prompt Types](#available-prompt-types)
  - [Contributing](#contributing)
  - [Testing](#testing)
  - [Versioning](#versioning)
  - [License](#license)
  - [Support](#support)
  - [Changelog](#changelog)
    - [v1](#v1)
      - [1.2.0 (2024-08-07)](#120-2024-08-07)
      - [1.1.0 (2024-08-06)](#110-2024-08-06)
      - [1.0.0 (2024-08-05)](#100-2024-08-05)

## Installation

FluxUtils requires Python 3.12 or higher. To install the latest version, use pip:

```sh
pip install fluxutils
```

This command will download and install FluxUtils along with its dependencies.

## Log Module

The Log module is the cornerstone of FluxUtils, offering a powerful and flexible logging system that can be tailored to suit a wide range of needs, from simple console output to complex multi-stream logging with custom formatting.

### Initialization

To start using the Logger, import it from `fluxutils.log` and create an instance:

```python
from fluxutils.log import Logger

logger = Logger()  # Initialize an instance of Logger
```

By default, the Logger is configured with sensible defaults, but you can customize its behavior during initialization or later through various methods.

### Logging Functions

The `Logger` class provides several logging functions to help with debugging and conveying information:

- `info`: For general information messages
- `debug`: For detailed debugging information
- `success`: For successful operation messages
- `warning`: For warning messages
- `error`: For error messages
- `lethal`: For critical error messages

Each logging function accepts the following parameters:

- `*values`: The values to be logged. You can pass multiple values, which will be concatenated into a single log message.
- `sep` (optional): A string inserted between values. Defaults to None.
- `rich` (optional): When set to `True`, formats the values for easier readability with syntax highlighting and other enhancements. The default value is `True`.

#### `*values`

The `*values` parameter allows you to log multiple objects in a single call, similar to Python's built-in `print` function. There's no need to put your objects in a list or tuple. All unnamed arguments are treated as values and will be joined together using the `sep` value.

Example:

```python
logger.info("User", username, action, f"@{datetime.now()}")
```

This flexibility allows for expressive and readable log statements.

#### `sep`

The `sep` argument is the string used to join two or more values together. When set to `None`, the default, each value will be printed with a space in between. To remove the space, set `sep` to `""`.

An example where the strings `"Hello"` and `"World"` will be joined with `" - "`:

```python
logger.info("Hello", "World", sep=" - ")  # Outputs: Hello - World
```

> **Note**: There's a known limitation where two or more trailing newline characters are treated as one. For example, `logger.info("Hello\n\n\n", "World!")` will produce the same output as `logger.info("Hello\n", "World!")`.

#### `rich`

The `rich` argument enables syntax formatting and highlighting for complex data types like lists, tuples, and dictionaries. When `rich` is set to `True` (the default), these data structures are formatted for improved readability:

```python
data = {"user": "John Doe", "actions": ["login", "view_profile", "logout"]}
logger.info("User activity:", data, rich=True)
```

This will output a nicely formatted and syntax-highlighted representation of the dictionary.

The specific rules for syntax formatting, highlighting, and color can be found in the Formatting ruleset. Additionally, the Formatting > Fixed Format Width rule allows you to specify a width for formatting lists, tuples, and dictionaries. If set to `0`, the width will automatically adjust to the remaining space in the terminal.

### Streams and File Handling

The Logger supports both console output and file streaming, allowing you to direct log messages to multiple destinations simultaneously. This is managed through a robust handler toolkit.

#### Adding and Removing Streams

You can add both console (standard output/error) and file streams to your logger:

```python
logger = Logger()

# Add a file stream
file_stream = logger.stream.file.add("application.log")

# Add stdout as a stream (this is added by default, but shown here for completeness)
stdout_stream = logger.stream.normal.add(sys.stdout)

# Remove a stream
logger.stream.file.remove("application.log")
logger.stream.normal.remove(sys.stdout)

# Remove a stream in a group
group.remove("log.log")

# Remove all streams in a group
group.remove_all()
```

#### Stream Groups

For more advanced management, you can create groups of streams:

```python
# Create a file group for multiple log files
file_group = logger.fhgroup(
    logger.stream.file.add("info.txt"),
    logger.stream.file.add("errors.log")
)

# Create a group for console streams
console_group = logger.shgroup(
    logger.stream.normal.add(sys.stdout),
    logger.stream.normal.add(sys.stderr)
)
```

These groups allow you to manage multiple streams collectively.

#### Modifying Stream Behavior

You can modify the behavior of individual streams or groups of streams:

```python
# Modify a single file stream
logger.stream.file.modify("application.log", ruleset={
    "timestamps": {
        "always_show": True,
        "use_utc": True,
    }
})

# Modify a group of streams
group.modify(ruleset={"log_line": {"format": "noalign"}})

# Modify console output settings
logger.stream.normal.modify(sys.stdout, ruleset={"formatting": {"ansi": False}})
```

#### Resetting Streams

You can reset file streams or groups, which clears their contents and reverts them to the default ruleset:

```python
# Reset a single file stream
logger.stream.file.reset("application.log")

# Reset a group of file streams
group.reset()
```

### Rules and Customization

The Logger's behavior is governed by a set of rules that can be customized to suit your needs. These rules control various aspects of logging, from timestamp formatting to message stacking.

#### Accessing and Modifying Rules

You can access and modify rules through the `ruleset` argument of your Logger stream/stream group:

```python
logger = Logger()

# Change rules for one stream
logger.stream.normal.modify(sys.stdout, ruleset={"timestamps": {"use_utc": True}})

# Change rules for multiple streams using a group
logger.stream.file.modify(logger.fhgroup("warnings.log", "debug.log"), ruleset={"timestamps": {"use_utc": True}})
```

#### Viewing Rules

To inspect the current rules or the default rules:

```python
# View default rules
logger.debug(logger.defaults)

# View currently applied rules
logger.debug(logger.ruleset.dict.all)

# View rules for a specific category
logger.debug(logger.ruleset.dict.stacking)
```

Replacing `.dict` with `.` will result in a `Ruleset` object instead of a dictionary. You can still retrieve single values as normal.

#### Rule Categories

The Logger's rules are organized into several categories, each controlling a different aspect of logging behavior:

1. **Timestamps**: Controls how and when timestamps are displayed.
2. **Stacking**: Manages the grouping of identical log messages. *Currently isn't supported.*
3. **Formatting**: Governs the visual presentation of log messages.
4. **Filtering**: Determines which messages are logged based on level and content.
5. **Output**: Configures default output streams.
6. **Metadata**: Controls the display of additional information alongside log messages.
7. **Log Line**: Defines the structure and content of each log line.

Each category can be accessed and modified individually, allowing for fine-grained control over the Logger's behavior.

### Customizing the Log Line

The Log Line > Format rule is particularly powerful, allowing you to define a custom template for how each log line is formatted. This template is processed by a robust templating engine, giving you precise control over the appearance and content of your log messages.

#### Premade Formats

For quick setup, you can use one of the premade formats by setting the Log Line > Format rule to a string:

- `"default"`: A balanced format suitable for most projects.
- `"filled"`: A variant with reversed background and foreground colors, creating a box-like view for increased legibility.
- `"noalign"`: Similar to the default view but without alignment parameters, useful for saving space.

An example where the sys.stdout stream's Log Line > Format is changed to `"filled"`:

```python
logger.stream.normal.modify(sys.stdout, ruleset={"log_line": {"format": "filled"}})
```

#### Custom Format Definition

For more control, you can define a custom format using a list of segment dictionaries. Each segment represents a part of the log line and can be either static text or a dynamic template.

Here's an example of a custom format:

```python
[
    {
        "type": "template",
        "value": "timestamp",
        "parameters": [{"color": {"foreground": "green"}}]
    },
    {"type": "static", "value": " "},
    {
        "type": "template",
        "value": "level",
        "parameters": [
            {"color": {"foreground": "default"}},
            {"case": "upper"},
            {"align": {"alignment": "left", "width": 7}}
        ]
    },
    {"type": "static", "value": " "},
    {
        "type": "template",
        "value": "filename",
        "parameters": [
            {"color": {"foreground": "magenta"}},
            {"truncate": {"width": 20, "position": "start"}}
        ]
    }
]
```

This format would create log lines with a green timestamp, followed by an uppercase, left-aligned log level, and then the filename in magenta, truncated to 20 characters from the start if necessary.

#### Segment Types

There are two types of segments:

1. **Static**: Defined with `"type": "static"` and a `"value"` key. These are fixed strings that appear in every log line.

2. **Template**: Defined with `"type": "template"` and a `"value"` key. These are dynamic elements that are replaced with actual data when the log line is generated. If you still want to use parameters on a string that changes often, you can pass it in using `"builtin": False`.

#### Built-in Templates

FluxUtils provides several built-in templates that you can use in your log line format:

- `timestamp`: The current time, formatted according to the Timestamp rules.
- `filename`: The name of the file where the log function was called.
- `wrapfunc`: The name of the function containing the log call (shows as `"<module>"` if not within a defined function).
- `linenum`: The line number of the log function call.
- `level`: The level of the log message (e.g., "info", "debug", "error").

You can also create custom templates by setting `"builtin": false` and providing your own string value.

#### Template Parameters

Template parameters allow you to define detailed instructions for the templating engine, such as colors, truncation, alignment, and more. These parameters are defined in the `parameters` key as a list of dictionaries.

Each parameter is a single-key dictionary, where the key is the parameter name and the value is a dictionary of arguments. For example, if you wanted to right-align a value to 15 characters, you can use the following:

```python
{"align": {"alignment": "right", "width": 15}}
```

By utilizing the below parameters, you can create a highly customized logging experience tailored to your specific needs and preferences.

1. `align`
   - **Adjusts the alignment and width of the segment text.**
   - `alignment`: String. Direction of alignment.
     - Default: `"left"`.
     - Options: `"left"`, `"right"`, `"center"`.
   - `width`: Integer. Minimum total space for alignment. Uses whichever is larger, the given width or the value length.
     - Default: `10`.
   - `fillchar`: String. Character to fill empty space.
     - Default: `" "`.

2. `case`
   - **Modifies the capitalization of the segment text.**
   - Options: `"upper"`, `"lower"`, `"capitalize"`, `"swapcase"`, `"title"`.

3. `filter`
   - **Allows inclusion or exclusion of specific content within the segment.**
   - `mode`: String. Filtering mode.
     - Default: `"exclude"`.
     - Options: `"exclude"`, `"include"`.
   - `items`: List of strings. Items to search for. Matching items will be replaced.
     - Default: `[]`.
   - `replace`: String. Replacement string for filtered items.
     - Default: `""`.

4. `affix`
   - **Adds prefix or suffix text to the segment.**
   - `prefix`: String. Text to prepend.
     - Default: `""`.
   - `suffix`: String. Text to append.
     - Default: `""`.

5. `truncate`
   - **Limits the length of the segment text, adding a marker to indicate truncation.**
   - `width`: Integer. Maximum allowed width before truncation.
     - Default: `10`.
   - `marker`: String. Truncation indicator.
     - Default: `"…"`.
   - `position`: String. Truncation position.
     - Default: `"end"`.
     - Options: `"start"`, `"middle"`, `"end"`.

6. `mask`
   - **Obscures part of the segment text, useful for sensitive information.**
   - `width`: Tuple of integers. Total width, width of unmasked text.
     - Default: `(10, 4)`.
   - `masker`: String. Character for masking.
     - Default: `"*"`.
   - `position`: String. Masking position.
     - Default: `"end"`.
     - Options: `"start"`, `"middle"`, `"end"`.

7. `pad`
   - **Adds padding to the left and/or right of the segment text.**
   - `left`: Integer. Left padding amount.
     - Default: `0`.
   - `right`: Integer. Right padding amount.
     - Default: `0`.
   - `fillchar`: String. Padding character.
     - Default: `" "`.

8. `repeat`
   - **Repeats the segment text a specified number of times.**
   - `count`: Integer. Number of times to repeat the value.
     - Default: `1`.

9. `if`
   - **Applies conditional formatting based on specified conditions.**
   - `condition`: Dictionary. Condition for action trigger.
     - `type`: String. Condition type.
       - Options: `"breakpoint"`, `"contains"`, `"excludes"`, `"matches"`, `"startswith"`, `"endswith"`.
     - `value`: Dictionary or List of strings. Condition value.
       - For `"breakpoint"`, dictionary formatted like `{"min": int, "max": int}`.
       - For `"contains"`, `"exactly"`, `"excludes"`, `"startswith"`, `"endswith"`, list of strings to check against.
   - `action`: Dictionary. Action to apply if condition is met.
     - `type`: String. Action type.
       - Options: `"parameters"`, `"set"`, `"replace"`.
     - `value`: List, String, or Dictionary. Action value.
       - For `"parameters"`, list of parameters (same as defined template segment parameters).
       - For `"set"`, string to set the value to.
       - For `"replace"`, dictionary formatted like `{"old": str, "new": str}`.

10. `visible`
    - **Controls the visibility of the segment. Applied out of order; last parameter to be calculated.**
    - Boolean, String, or Integer.
      - If Boolean, visibility directly correlates to value.
      - If String, must be formatted `{">"|"<"}{integer}`. Visibility determined if expression is true when compared to terminal width.
      - If Integer, treated as `>{integer}`. See String case.

11. `color`
    - **Sets the text and background colors of the segment. Applied out of order; last parameter to be calculated.**
    - `foreground`: Tuple of integers or String. Sets text color.
      - If Tuple, each value corresponds to red, green, and blue.
      - If String, color is determined by preset color options, or white if color is invalid.
      - Default: `"white"`.
    - `background`: Tuple of integers or String. Sets background color.
      - If Tuple, each value corresponds to red, green, and blue.
      - If String, color is determined by preset color options, or white if color is invalid.
      - Default: `"white"`.
    - Preset color options: `"white"`, `"black"`, `"blue"`, `"cyan"`, `"green"`, `"magenta"`, `"yellow"`, `"red"`.

12. `style`
    - **Applies various text styles to the segment.**
    - `bold`: Boolean. Applies bold formatting.
      - Default: `False`.
    - `italic`: Boolean. Applies italic formatting.
      - Default: `False`.
    - `underline`: Boolean. Applies underline formatting.
      - Default: `False`.
    - `blink`: Boolean. Applies blink formatting.
      - Default: `False`.
    - `reverse`: Boolean. Applies reverse formatting.
      - Default: `False`.

Parameters are processed in the order they appear, except for the `color`, and `visible` parameters, which are always processed last.

### Advanced Usage

#### Multiple Streams with Different Configurations

You can set up multiple output streams, each with its own configuration:

```python
logger = Logger()

# Configure a file stream with timestamps always shown
file_stream = logger.stream.file.add("detailed_log.log")
logger.stream.file.modify(file_stream, {
    "timestamps": {"always_show": True},
    "formatting": {"log_line": "noalign"}
})

# Configure stdout with color but no timestamps
logger.stream.normal.modify(sys.stdout, {
    "timestamps": {"always_show": False},
    "formatting": {"log_line": "filled"}
})

# Log a message - it will appear differently in each stream
logger.info("This message appears in both streams with different formatting")
```

#### Dynamic Formatting Based on Terminal Size

You can use the `if` parameter with the `breakpoint` condition to apply different formatting based on the terminal size:

```python
[
    {
        "type": "template",
        "value": "filename",
        "parameters": [
            {"if": {
                "condition": {"type": "breakpoint", "value": {"min": 100}},
                "action": {"type": "parameters", "value": [
                    {"truncate": {"width": 30, "position": "start"}}
                ]}
            }},
            {"if": {
                "condition": {"type": "breakpoint", "value": {"max": 100}},
                "action": {"type": "parameters", "value": [
                    {"truncate": {"width": 15, "position": "end"}}
                ]}
            }}
        ]
    }
]
```

This configuration will show more of the filename on wider terminals and less on narrower ones.

#### Custom Logging Levels

While FluxUtils doesn't directly support creating custom logging levels, you can achieve similar functionality by modifying the log line format to replace an existing log level with a new one:

```python
[
    {
        "type": "template",
        "value": "level",
        "parameters": [
            {"if": {
                "condition": {"type": "matches", "value": ["info"]},
                "action": {"type": "set", "value": "CUSTOM"}
            }},
            {"color": {"foreground": "cyan"}},
            {"affix": {"prefix": "[", "suffix": "]"}}
        ]
    },
    {"type": "static", "value": " "},
    {"type": "template", "value": "message"}
]

logger.info("[CUSTOM] This is a custom level message")
```

This approach allows you to create pseudo-custom levels while still using the built-in logging functions.

## Decorators Module

FluxUtils provides a set of powerful decorators to enhance your Python functions. These decorators offer various functionalities such as retry mechanisms, timeout handling, rate limiting, and more.

### retry

Retries the decorated function a specified number of times with a delay between attempts.

```python
from fluxutils.decorators import retry

@retry(max_retries=3, delay=1.0)
def flaky_function():
    # Your code here
    # If an exception is raised, the function will be retried up to 3 times
    # with a 1-second delay between attempts
```

### retry_exponential_backoff

Similar to `retry`, but with an exponential backoff delay between attempts.

```python
from fluxutils.decorators import retry_exponential_backoff

@retry_exponential_backoff(max_retries=3, initial_delay=1.0)
def flaky_function():
    # Your code here
    # If an exception is raised, the function will be retried up to 3 times
    # with delays of 1, 2, and 4 seconds between attempts
```

### timeout

Sets a maximum execution time for the decorated function.

```python
from fluxutils.decorators import timeout

@timeout(seconds=5)
def long_running_function():
    # Your code here
    # If the function doesn't complete within 5 seconds, a TimeoutError will be raised
```

### rate_limiter

Limits the rate at which the decorated function can be called.

```python
from fluxutils.decorators import rate_limiter

@rate_limiter(calls=5, period=60, immediate_fail=True)
def rate_limited_function():
    # Your code here
    # This function can only be called 5 times per 60 seconds
    # If called more frequently, it will raise a RateLimitError
```

### trace

Logs the function call, its arguments, and the return value.

```python
from fluxutils.decorators import trace

@trace
def function_to_trace(arg1, arg2):
    # Your code here
    # The function call, arguments, and return value will be printed
```

### suppress_exceptions

Catches and suppresses any exceptions raised by the decorated function.

```python
from fluxutils.decorators import suppress_exceptions

@suppress_exceptions
def risky_function():
    # Your code here
    # Any exceptions raised will be caught and suppressed
```

### deprecated

Marks a function as deprecated and issues a warning when it's used.

```python
from fluxutils.decorators import deprecated

@deprecated
def old_function():
    # Your code here
    # A deprecation warning will be issued when this function is called
```

### type_check

Checks the types of arguments and return value against specified types.

```python
from fluxutils.decorators import type_check

@type_check(arg_types=(int, str), return_type=str)
def typed_function(num: int, text: str) -> str:
    # Your code here
    # The decorator will check if num is an int, text is a str,
    # and the return value is a str
```

### log_execution_time

Logs the execution time of the decorated function.

```python
from fluxutils.decorators import log_execution_time

@log_execution_time
def timed_function():
    # Your code here
    # The execution time of this function will be logged
```

### cache

Caches the return value of the function based on its arguments.

```python
from fluxutils.decorators import cache

@cache
def expensive_function(arg):
    # Your code here
    # The return value will be cached based on the 'arg' value
```

### requires_permission

Checks if the user has the required permission before executing the function.

```python
from fluxutils.decorators import requires_permission

@requires_permission("admin")
def admin_function(user):
    # Your code here
    # This function will only execute if the user has "admin" permission
```

## CLI Module

FluxUtils includes a CLI (Command Line Interface) module that allows you to easily create interactive command-line applications. This module provides tools for building CLIs with argument parsing and command management.

### Basic Usage

Here's a comprehensive example of how to create a CLI application using FluxUtils, demonstrating the use of both `@argument` and `@option`:

```python
from fluxutils.cli import CLI, argument, option

cli = CLI()  # Create a CLI instance

@cli.command
@argument("name", help="Name to greet")  # Required positional argument
@option("--greeting", default="Hello", help="Greeting to use")  # Optional option with default
@option("--shout", is_flag=True, help="Print in uppercase")  # Optional flag
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message

if __name__ == '__main__':
    cli.run()
```

#### How It Works

In this example:

- We create a `CLI` instance.
- We define a `greet` command using the `@cli.command` decorator.
- We add a required `name` argument using the `@argument` decorator. This is a positional argument.
- We add an optional `--greeting` option using the `@option` decorator. This option has a default value of "Hello".
- We add an optional `--shout` flag using the `@option` decorator. This is a boolean flag.
- The `greet` function contains the logic for the command.
- We call `cli.run()` to start the CLI application. You can run the application multiple times if you wish to.

#### Running Your Application

You can run this CLI in various ways:

```zsh
python your_script.py greet Alice
# -> "Hello, Alice!"
python your_script.py greet "Bob Jr." --greeting Hi
# -> "Hi, Bob. Jr!"
python your_script.py greet John --shout
# -> "HELLO, JOHN!"
python your_script.py greet Baby --greeting "Hasta la vista" --shout
# -> "HASTA LA VISTA, BABY!"
```

#### Key Points

1. `@argument` is used for required positional arguments. In this case, `name` must always be provided.

2. `@option` is used to define command-line options. These are typically optional and are prefixed with `--` (or `-` for short versions).
   - The `--greeting` option is optional and has a default value.
   - The `--shout` option is a flag (boolean) that doesn't require a value.

3. Options defined with `@option` can be required or optional, depending on how you configure them. In this example, both are optional.

This structure allows for flexible and intuitive command-line interfaces, where users can provide required arguments and optionally customize behavior with additional options.

### Interactive Prompts

The CLI module also includes an API for creating interactive prompts:

```python
from fluxutils.cli import CLI, Prompt

cli = CLI()

@cli.command
def setup():
    """Interactive setup command"""
    name = Prompt.text("What's your name?").ask()
    age = Prompt.number("How old are you?").min(0).max(120).ask()
    likes_pizza = Prompt.confirm("Do you like pizza?").ask()
    favorite_color = Prompt.choice("What's your favorite color?", choices=['Red', 'Green', 'Blue']).ask()
    hobbies = Prompt.checkbox("Select your hobbies:", choices=['Reading', 'Gaming', 'Sports', 'Cooking']).ask()
    
    print(f"Name: {name}")
    print(f"Age: {age}")
    print(f"Likes pizza: {likes_pizza}")
    print(f"Favorite color: {favorite_color}")
    print(f"Hobbies: {', '.join(hobbies)}")

if __name__ == '__main__':
    cli.run()
```

This setup command will interactively prompt the user for various pieces of information.

### Available Prompt Types

- `Prompt.text()`: For text input
  - Includes default method
- `Prompt.password()`: For hidden password input
- `Prompt.confirm()`: For yes/no questions
  - Includes default method
- `Prompt.choice()`: For selecting one item from a list
- `Prompt.checkbox()`: For selecting multiple items from a list
- `Prompt.number()`: For numeric input
  - Includes default method, as well as min and max methods

Each prompt type has an `ask()` method that displays the prompt and returns the user's input.

By using these features of the FluxUtils CLI module, you can create command-line applications with intuitive argument parsing and interactive prompts. This allows for more user-friendly and flexible command-line interfaces in your Python projects.

## Contributing

Contributions to FluxUtils are welcome! Whether you're fixing bugs, improving documentation, or proposing new features, your efforts are appreciated. Here's how you can contribute:

1. **Fork & Clone the Repository**: Start by forking the FluxUtils repository on GitHub. Clone your fork to your local machine for development.

   ```zsh
   git clone https://github.com/<your-name>/fluxutils.git
   ```

2. **Create a Branch**: Create a new branch for your feature or bug fix.

   ```zsh
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes & Test**: Implement your feature or bug fix. Be sure to test it before continuing.
4. **Update Documentation**: If your changes require it, update the README and any relevant documentation.
5. **Commit Your Changes**: Commit your changes with a clear and descriptive commit message.

   ```zsh
   git commit -m "Add feature: your feature description"
   ```

6. **Push to Your Fork**: Push your changes to your fork on GitHub.

   ```zsh
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**: Go to the FluxUtils repository on GitHub and create a new pull request from your feature branch.

Please ensure your code adheres to the project's coding standards and includes appropriate documentation. We appreciate your contribution!

## Testing

FluxUtils uses unittest for its test suite. We encourage contributors to write tests for new features and bug fixes. The `fluxutils/tests/decorators/test1.py` provides a good example of how to structure tests.

## Versioning

FluxUtils follows [Semantic Versioning](https://semver.org/). The version number is structured as MAJOR.MINOR.PATCH:

- MAJOR version increments denote incompatible API changes,
- MINOR version increments add functionality in a backwards-compatible manner, and
- PATCH version increments are for backwards-compatible bug fixes.

## License

FluxUtils is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

<!-- ## Acknowledgements

We would like to thank all the contributors who have helped to make FluxUtils better. Your time and effort are greatly appreciated. -->

## Support

If you encounter any issues or have questions about using FluxUtils, please file an issue on the [GitHub issue tracker](https://github.com/DomBom16/fluxutils/issues).

## Changelog

### v1

#### 1.2.0 (2024-08-07)

- Added new `decorators` module with the following decorators:
  - `retry`: Retries a function with a specified number of attempts and delay.
  - `retry_exponential_backoff`: Retries with exponential backoff delay.
  - `timeout`: Sets a maximum execution time for a function.
  - `rate_limiter`: Limits the rate of function calls.
  - `trace`: Logs function calls, arguments, and return values.
  - `suppress_exceptions`: Catches and suppresses exceptions.
  - `deprecated`: Marks functions as deprecated with warnings.
  - `type_check`: Checks argument and return value types.
  - `log_execution_time`: Logs function execution time.
  - `cache`: Caches function return values.
  - `requires_permission`: Checks user permissions before execution.
- Added new `cli` module with the following features:
  - `CLI` class for creating command-line interfaces
  - `@command` decorator for defining CLI commands
  - `@argument` decorator for adding required positional arguments
  - `@option` decorator for adding optional command-line options
  - `Prompt` class with various interactive prompt types:
    - `text`: For text input
    - `password`: For hidden password input
    - `confirm`: For yes/no questions
    - `choice`: For selecting one item from a list
    - `checkbox`: For selecting multiple items from a list
    - `number`: For numeric input with optional min/max values
- Improved documentation:
  - Added comprehensive examples for using the `decorators` module
  - Expanded explanation of the `cli` module with detailed usage examples
  - Updated README with new sections for Decorators and CLI modules
- Added basic test suite for new modules
- Updated package dependencies

#### 1.1.0 (2024-08-06)

- Updated `log` module
  - Added `TestLogger` class for bare-bones testing
  - Fixed a bug where only ANSI escape sequences were removed from the message when Formatting > ANSI was set to `False`
  - Fixed `add` and `modify` methods for `StreamHandler` for easier configuration updates
  - Refactored `FileHandler`
  - Added robust nesting support for `fhgroup` and `shgroup`
  - Added support for multiple simultaneous streams with individual configurations
  - Updated `strip_ansi` utility
  - Turned `test1.py` into a more robust test environment
  - Added `test2.py` to `tests` which executes `TestLogger`
- Added changelog, support, license, versioning, testing, and contributing sections to README
- Improved `Logger` documentation
  - Significantly expanded README with detailed explanations and examples
  - Added advanced usage scenarios and best practices

#### 1.0.0 (2024-08-05)

- Initial release of FluxUtils
- Introduced `log` module with basic logging functionality

---

Thank you for using FluxUtils! We hope it enhances your Python development experience and makes development more powerful and flexible in your projects.
