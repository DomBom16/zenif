# Log Module

The Log module is the cornerstone of Zenif, offering a powerful and flexible logging system that can be tailored to suit a wide range of needs, from simple console output to complex multi-stream logging with custom formatting.

## Initialization

To start using the Logger, import it from `zenif.log` and create an instance:

```python
from zenif.log import Logger

logger = Logger()  # Initialize an instance of Logger
```

By default, the Logger is configured with sensible defaults, but you can customize its behavior during initialization or later through various methods.

## Logging Functions

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

### Arguments

The `*values` argument allows you to log multiple objects in a single call, similar to Python's built-in `print` function. There's no need to put your objects in a list or tuple. All unnamed arguments are treated as values and will be joined together using the `sep` value.

Example:

```python
logger.info("User", username, action, f"@{datetime.now()}")
```

This flexibility allows for expressive and readable log statements.

The `sep` argument is the string used to join two or more values together. When set to `None`, the default, each value will be printed with a space in between. To remove the space, set `sep` to `""`.

An example where the strings `"Hello"` and `"World"` will be joined with `" - "`:

```python
logger.info("Hello", "World", sep=" - ")  # Outputs: Hello - World
```

> **Note**: There's a known limitation where two or more trailing newline characters are treated as one. For example, `logger.info("Hello\n\n\n", "World!")` will produce the same output as `logger.info("Hello\n", "World!")`.

The `rich` argument enables syntax formatting and highlighting for complex data types like lists, tuples, and dictionaries. When `rich` is set to `True` (the default), these data structures are formatted for improved readability:

```python
data = {"user": "John Doe", "actions": ["login", "view_profile", "logout"]}
logger.info("User activity:", data, rich=True)
```

This will output a nicely formatted and syntax-highlighted representation of the dictionary.

The specific rules for syntax formatting, highlighting, and color can be found in the Formatting ruleset. Additionally, the Formatting > Fixed Format Width rule allows you to specify a width for formatting lists, tuples, and dictionaries. If set to `0`, the width will automatically adjust to the remaining space in the terminal.

## Streams and File Handling

The Logger supports both console output and file streaming, allowing you to direct log messages to multiple destinations simultaneously. This is managed through a robust handler toolkit.

### Adding and Removing Streams

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

### Stream Groups

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

### Modifying Stream Behavior

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

### Resetting Streams

You can reset file streams or groups, which clears their contents and reverts them to the default ruleset:

```python
# Reset a single file stream
logger.stream.file.reset("application.log")

# Reset a group of file streams
group.reset()
```

## Rules and Customization

The Logger's behavior is governed by a set of rules that can be customized to suit your needs. These rules control various aspects of logging, from timestamp formatting to message stacking.

### Accessing and Modifying Rules

You can access and modify rules through the `ruleset` argument of your Logger stream/stream group:

```python
logger = Logger()

# Change rules for one stream
logger.stream.normal.modify(sys.stdout, ruleset={"timestamps": {"use_utc": True}})

# Change rules for multiple streams using a group
logger.stream.file.modify(logger.fhgroup("warnings.log", "debug.log"), ruleset={"timestamps": {"use_utc": True}})
```

### Viewing Rules

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

### Rule Categories

The Logger's rules are organized into several categories, each controlling a different aspect of logging behavior:

1. **Timestamps**: Controls how and when timestamps are displayed.
2. **Stacking**: Manages the grouping of identical log messages. _Currently isn't supported._
3. **Formatting**: Governs the visual presentation of log messages.
4. **Filtering**: Determines which messages are logged based on level and content.
5. **Output**: Configures default output streams.
6. **Metadata**: Controls the display of additional information alongside log messages.
7. **Log Line**: Defines the structure and content of each log line.

Each category can be accessed and modified individually, allowing for fine-grained control over the Logger's behavior.

## Customizing the Log Line

The Log Line > Format rule is particularly powerful, allowing you to define a custom template for how each log line is formatted. This template is processed by a robust templating engine, giving you precise control over the appearance and content of your log messages.

### Premade Formats

For quick setup, you can use one of the premade formats by setting the Log Line > Format rule to a string:

- `"default"`: A balanced format suitable for most projects.
- `"filled"`: A variant with reversed background and foreground colors, creating a box-like view for increased legibility.
- `"noalign"`: Similar to the default view but without alignment parameters, useful for saving space.

An example where the sys.stdout stream's Log Line > Format is changed to `"filled"`:

```python
logger.stream.normal.modify(sys.stdout, ruleset={"log_line": {"format": "filled"}})
```

### Custom Format Definition

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

### Segment Types

There are two types of segments:

1. **Static**: Defined with `"type": "static"` and a `"value"` key. These are fixed strings that appear in every log line.

2. **Template**: Defined with `"type": "template"` and a `"value"` key. These are dynamic elements that are replaced with actual data when the log line is generated. If you still want to use parameters on a string that changes often, you can pass it in using `"builtin": False`.

### Built-in Templates

Zenif provides several built-in templates that you can use in your log line format:

- `timestamp`: The current time, formatted according to the Timestamp rules.
- `filename`: The name of the file where the log function was called.
- `wrapfunc`: The name of the function containing the log call (shows as `"<module>"` if not within a defined function).
- `linenum`: The line number of the log function call.
- `level`: The level of the log message (e.g., "info", "debug", "error").

You can also create custom templates by setting `"builtin": false` and providing your own string value.

### Template Parameters

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

## Advanced Usage

### Multiple Streams with Different Configurations

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

### Dynamic Formatting Based on Terminal Size

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

### Custom Logging Levels

While Zenif doesn't directly support creating custom logging levels, you can achieve similar functionality by modifying the log line format to replace an existing log level with a new one:

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
