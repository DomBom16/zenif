# CLI Module

Zenif includes a CLI (Command Line Interface) module that allows you to easily create interactive command-line applications. This module provides tools for building CLIs with argument parsing, command management, and now includes schema integration for robust input validation.

## Basic Usage

Here's a comprehensive example of how to create a CLI application using Zenif, demonstrating the use of both `@arg` and `@kwarg`:

```python
from zenif.cli import CLI, arg, kwarg

cli = CLI(name="demo")  # Create a CLI instance, optionally with a name

@cli.command
@arg("name", help="Name to greet")  # Required positional argument
@kwarg("--greeting", default="Hello", help="Greeting to use")  # Optional option with default
@kwarg("--shout", is_flag=True, help="Print in uppercase")  # Optional flag
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message

if __name__ == '__main__':
    cli.run()
```

## Setting Up ZSH Commands for Your Users

The CLI module comes with a handy method that let's your users install the given file as a .zshrc function. By importing and running the `install_setup_command()` method, your users can run `python yourfile.py setup --alias youralias` to simplify the command line interaction.

```python
from zenif.cli import CLI, install_setup_command
import os

cli = CLI()
install_setup_command(cli=cli, script_path=os.path.abspath(__file__))
```

## Available Prompt Types

- `Prompt.text()`: For text input (works with String schema fields)
- `Prompt.password()`: For hidden password input (works with String schema fields)
- `Prompt.confirm()`: For yes/no questions (works with Boolean schema fields)
- `Prompt.choice()`: For selecting one item from a list (works *only* with String schema fields)
- `Prompt.checkbox()`: For selecting multiple items from a list (works with List schema fields)
- `Prompt.number()`: For numeric input (works with Integer or Float schema fields)
- `Prompt.date()`: For dates (works with String schema fields)

## Special Prompt Methods

### `default()`

Available for the `text`, `confirm`, and `number` types. If a default is given, the user can submit an empty field and the default value will be used as their submission.

### `peeper()`

Available for the `password` type. When enabled, masked inputs will show the last character if it was just typed. If `Space` or `Backspace` are pressed, the last character of the input will not be visible. After submitting, the "peeper" character will not be visible.

### `commas()`

Available for the `number` type. When enabled, the input shown after the prompt will insert commas (Ex: `12345` -> `12,345`). This will not affect the number returned on submit. Cannot be enabled alongside `allow_decimals()`.

### `allow_decimals()`

Available for the `number` type. When enabled, decimal values are able to be inputted. Until the `.` character is typed, a dim `.` character will trail the inputted number. After a `.` character is typed, the `.` will no longer appear dim and no other `.`s can be added to the input until the existing one is removed from the input. Cannot be enabled alongside `commas()`.

### `allow_negatives()`

Available for the `number` type. When enabled, negative values are able to be inputted. Pressing the `-` key will have no effect until at least one digit is inputted. Upon pressed, the sign in front of the value will be toggled (an implicit positive sign is used). If all numeric digits are removed, the `-` sign will dissappear.

### `month_first()`

Available for the `date` type. When enabled, the date will be inputted in the format month-day-year instead of day-month-year.

### `year_range()`

Available for the `date` type. The `year_range` is the defined minimun and maximum values that the year must be in between, inclusive on both ends. By default, the range is from `1900` to `2100`.

### `separator()`

Available for the `date` type. Used as the separator between the day, month, and year fields. By default, the `"/"` seperator is used.

### `show_words()`

Available for the `date` type. When enabled, the date shown beside the prompt upon submission will be displayed in words. Ex: 1/1/2014 -> January 1, 2014

## Getting Used To Input Controls

For the most part, input types that feature somewhat non-trivial controls will have them listed. However, each prompt type comes with it's own nuances that aren't included in the controls list for conciseness.

### Text Inputs

Press `Escape` to clear the current value.

### Number Inputs

Use `↑` to increase and `↓` to decrease the value.

### Date Inputs

Use `↑` to increase and `↓` to decrease the selected field.
Pressing `Shift` + `Tab` will act like the `Tab` functionality, but highlight fields in the opposite direction.

## Interactive Prompts with Schema Validation

The CLI module is now able to be integrated with the Schema module to validate your inputs in real-time:

```python
from zenif.cli import CLI, Prompt, schemafy
from zenif.schema import Schema, StringF, IntegerF, ListF, Length, Value

cli = CLI()

user_schema = Schema(
    name=StringF()
         .name("name")
         .has(NotEmpty()),
    password=StringF()
            .name("password")
            .has(Length(min=3, max=50))
    age=IntegerF()
        .name("age")
        .has(Value(min=18, max=120)),
    salary=IntegerF()
           .name("salary")
           .has(Value(min=0)),
    interests=ListF()
              .name("interests")
              .item_type(StringF())
              .has(Length(min=1, max=5))
)

@cli.command
def setup():
    """Interactive setup command with schema validation"""
    name = Prompt.text("Enter your name", schema=user_schema, id="name").ask()
    age = Prompt.number("Enter your age", schema=user_schema, id="age").ask()
    password = Prompt.password("Enter your password", schema=user_schema, id="password").peeper().ask()
    # .commas() will add commas only visually (not the the returned value). Ex: 12345 -> 12,345
    salary = Prompt.number("What's your salary?", schema=user_schema, id="salary").commas().ask()
    interests = Prompt.checkbox("Select your interests",
                                choices=["Reading", "Gaming", "Sports", "Cooking", "Travel"],
                                schema=user_schema,
                                id="interests").ask()

    print(f"Name: {name}")
    print(f"Age: {age}")
    print(f"Salary: {salary}")
    print(f"Interests: {', '.join(interests)}")

if __name__ == '__main__':
    cli.run()
```

When using schemas with the CLI module, make sure that your `Schema` arguments match the `id` argument passed into the `Prompt` method.

## Schema Integration

When using prompts with schemas:

- The schema validates the input in real-time, providing immediate feedback to the user.
- Users cannot proceed until they provide valid input according to the schema.
- Error messages from the schema validation are displayed inline to the right of the users cursor.

For more detailed information on creating and using schemas, please refer to the [schema documentation](./schema.md).
