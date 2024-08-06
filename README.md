# FluxUtils

`fluxutils` is a simple yet customizable and versatile module designed to provide various utilities that enhance the efficiency and performance of your programs. Whether you are a seasoned developer or just starting out, `fluxutils` offers tools that help streamline your workflow and improve code management.

## Installation

You can easily install `fluxutils` using pip, ensuring you have access to the latest features and updates. Note that `fluxutils` requires Python 3.12 or higher to function properly. To install, run the following command in your terminal:

```sh
pip install fluxutils
```

## Logger

One of the standout features of `fluxutils` is its logger, which is incredibly useful for both debugging and providing informative messages to users during various processes, such as app installations or complex computations. To get started with the logger, import it from `fluxutils.log`:

```py
from fluxutils.log import Logger

l = Logger()  # Initalize an instance of Logger
```

The logger is designed to be easy to use while offering a high degree of customization, allowing you to tailor it to your specific needs.

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
- `sep` (optional): A string inserted between values. Defaults to a space.
- `rich` (optional): When set to `True`, formats the values for easier readability with syntax highlighting and other enhancements. The default value is `True`.

#### `*values`

When logging a multitude of objects to the console, you can do so just like Python's native `print` function; there's no need to put your objects in a list or tuple. Instead all unnamed arguments are treated as a value, and will be joined together by the `sep` value.

#### `sep`

The `sep` argument is the string that joins 2 or more values together. When set to `None`, each value will be printed one next to the other.

> **Note**
> A known bug causes 2 or more trailing newline characters, to be treated as one. For example, calling `Logger().info("Hello\n\n\n", "World!")` is the same as calling `Logger().info("Hello\n", "World!")`

#### `rich`

The `rich` argument enables syntax formatting and highlighting for list, tuple, and dictionary data types. Rules for syntax formatting, highlighting, and color can be found in the Formatting ruleset. Additionally, the Formatting > Fixed Format Width rule allows you to provide a width to format lists, tuples, and dictionaries to. If set to `0`, the width will be set to the remaining space in the terminal.

### Streams and File Handling

The logger supports both console output and file streaming using a robust handler toolkit.

```py
l = Logger()

# Add a file stream
file_stream = l.stream.file.add("log.log")

# Create a file group for multiple log files
file_group = l.fhgroup(l.stream.file.add("log1.log"), l.stream.file.add("log2.log"))
# You can do the same thing with console streams as well!
stream_group = l.shgroup(l.stream.normal.add(sys.stdout), l.stream.normal.add(sys.stderr))

# Reset group; clears contents and reverts to default ruleset
file_group.reset()
stream_group.reset()

# Modify group settings
file_group.modify(ruleset={
    "timestamps": {
        "always_show": True,
        "use_utc": True,
    },
    "log_line": {"format": "noalign"},
})

# Modify console output settings
l.stream.normal.modify(sys.stdout, ruleset={"timestamps": {"always_show": True}})

# Remove a file stream
l.stream.file.remove("log.log")
```

### Rules

The `Logger` class also allows you to define custom rules that override the default settings, giving you control over how log messages are formatted and displayed. For instance, to enable stacking of identical log messages, you can set the `rules` argument like so:

```python
l = Logger()

# Enable message stacking
l.ruleset.stacking.enabled = True

# Change timestamp format
l.ruleset.timestamps.always_show = True
l.ruleset.timestamps.use_utc = True

# Modify log line format
l.ruleset.log_line.format = "noalign"
```

Additionally, if you want to view the default rules or the currently applied rules, you can use the respective `defaults` and `ruleset.dict.all` variables:

- `defaults` provides the default rules.
- `ruleset.dict.all` provides the currently applied rules.

```py
from fluxutils.log import Logger

l = Logger()  # Initialize an instance of Logger

l.debug(l.defaults)  # View default rules
l.debug(l.ruleset.dict.all)  # View currently applied rules
l.debug(l.ruleset.dict.stacking)  # View specific rule category
```

You can also access individual rule categories as dictionaries:

```py
# Access the stacking ruleset as a dictionary
print(l.ruleset.dict.stacking)
```

This structure allows you to have granular control over the logging behavior and easily view or modify the rules as needed.

### Customizing the Log Line

The `Logger` in `fluxutils` includes many built-in rules for customization, but the Log Line > Format rule stands out for its versatility. This rule allows you to customize the information displayed in each log entry using a robust templating engine.

#### Premade Formats

If you are in a hurry or it isn't worth the hassle, you can use the prebuilt formats by defining the Log Line > Format rule as a string instead.

- `default`: Sets the default log line. Great for most projects.
- `filled`: A variant where the background and foreground colors have been reversed, displaying a box-like view. Great for increasing legibility.
- `noalign`: The default view without any alignment parameters. Great for saving space.

#### Segment Types

Each segment is defined as a dictionary within the outer list. The segment `type` can be either `static` or `template`.

Static segments are defined with the `value` key and are useful as separators or fixed text. They cannot have parameters applied and serve as constant elements in your log messages.

Template segments are also defined with the `value` key but offer much more flexibility. They can include built-in templates like timestamps, filenames, or custom variables, making your log messages more informative and context-aware.

#### Built-in Templates

Some of the built-in templates available for use in `fluxutils` include:

- `timestamp`: The logging time, formatted according to the Timestamp > Format rule.
- `filename`: The name of the file where the log function was called.
- `wrapfunc`: The function housing the log call origin (returns `"<module>"` if not within a defined function).
- `linenum`: The line number of the called log function.
- `level`: The level of the log function call (e.g., info, debug).

For more specific needs, you can set the `builtin` key to `False` and pass in a custom string.

#### Template Parameters

Template parameters allow you to define detailed instructions for the templating engine, such as colors, truncation, alignment, and more. These parameters are defined in the `parameters` key as a list of dictionaries.

Each parameter is a single-key dictionary, where the key is the parameter name and the value is a dictionary of arguments. For example, if you wanted to right-align a value to 15 characters, you can use the following:

```python
{"align": {"alignment": "right", "width": 15}}
```

Parameters are applied in the order they appear, except for the `color`, and `visible` parameters, which are always calculated last even if placed inside an `if` parameter.

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

## Contributing

Contributions to `fluxutils` are welcome! Please refer to our contribution guidelines for more information on how to submit pull requests, report issues, or request features.

## License

`fluxutils` is released under the MIT License. See the LICENSE file for more details.
