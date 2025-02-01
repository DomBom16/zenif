# CLI Module

Zenif includes a CLI (Command Line Interface) module that allows you to easily create interactive command-line applications. This module provides tools for building CLIs with argument parsing, command management, and now includes schema integration for robust input validation, as well as tooling for interactive prompts in the terminal.

## Table of Contents

- [CLI Module](#cli-module)
  - [Table of Contents](#table-of-contents)
  - [Getting Started with Applets](#getting-started-with-applets)
    - [Setting Up ZSH Commands for Your Users](#setting-up-zsh-commands-for-your-users)
  - [Getting Started with Prompts](#getting-started-with-prompts)
    - [Basic Usage](#basic-usage)
    - [Types of Prompts](#types-of-prompts)
  - [Interactive Prompts with Schema Validation](#interactive-prompts-with-schema-validation)
  - [Special Callback Decorators](#special-callback-decorators)

## Getting Started with Applets

Here's a comprehensive example of how to create a CLI application using Zenif, demonstrating the basic capabilites of Zenif's CLI applets.

First, import the required modules from the Zenif library and initialize an instance.

```py
from zenif.cli import CLI, req, opt

cli = CLI(name="applets-demo")
```

The `CLI` class is the core component that defines the command-line interface. The `req` and `opt` decorators are used to specify required and optional arguments.

Register a function as a command within the CLI using the `@cli.command` decorator. This tells Zenif that the function below will be a CLI command. In this case, the function name greet becomes the command name that users will invoke.

```py
@cli.command()
def greet():
    ...
```

Use `@req` to define a required argument that the user must provide.

```python
@req("name", help="Name to greet")
```

Here, `"name"` is the required argument, meaning the user must enter a name when running the command. The help parameter provides a description for --help output.

Similarly, we can use `@opt` to define an optional argument.

```python
@opt("--greeting", default="Hello", help="Greeting to use")
```

This optional argument `--greeting` allows the user to specify a custom greeting. If no greeting is provided, it defaults to `"Hello"`.

`@opt` can also be used to create flags. Use `@opt` with `is_flag=True` to define a flag that enables a specific behavior.

```python
@opt("--shout", is_flag=True, help="Print in uppercase")
```

Unlike regular options, this flag does not require a value. If `--shout` is included in the command, its value is `True`; otherwise, it remains `False`.

Now, implement the actual function that processes user input.

```python
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message # This will be printed to the terminal.
```

The function takes in the `name`, `greeting`, and `shout` parameters. It constructs a greeting message and converts it to uppercase if the `--shout` flag is set to `True`. The return value is automatically displayed in the terminal. It's also good to use docstrings for all your commands as they are used to provide insightful information for the `--help` command.

However, running this script won't activite our function yet. We need to pass the `cli.run()` method to activite the CLI.

```python
if __name__ == "__main__":
    cli.run()
```

Now that the CLI is set up, users can interact with it as follows:

```bash
python script.py greet Alice
# Output: Hello, Alice!
python script.py greet Alice --greeting "Hi"
# Output: Hi, Alice!
python script.py greet Alice --shout
# Output: HELLO, ALICE!
```

Here's the code put together.

```python
from zenif.cli import CLI, req, opt

cli = CLI(name="demo")  # Create a CLI instance, optionally with a name

@cli.command
@req("name", help="Name to greet")  # Required positional argument
@opt("--greeting", default="Hello", help="Greeting to use")  # Optional option with default
@opt("--shout", is_flag=True, help="Print in uppercase")  # Optional flag
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message  # Logged to the terminal

if __name__ == '__main__':
    cli.run()  # Activate the CLI when the file is run
```

### Setting Up ZSH Commands for Your Users

The CLI module comes with a handy method that let's your users install the given file as a .zshrc function. By importing and running the `install_setup()` method, your users can run `python yourfile.py setup --alias youralias` to simplify the command line interaction, creating an alias within their `~/.zshrc` configuration.

```python
from zenif.cli import CLI, install_setup
import os

cli = CLI()
install_setup(cli=cli, script_path=os.path.abspath(__file__))
```

## Getting Started with Prompts

Zenif provides a flexible prompting system for interactive CLI applications. Prompts allow you to collect user input dynamically with built-in validation and formatting.

### Basic Usage

To use prompts in your CLI application, import the `Prompt` class and set up a CLI command like we did earlier:

```python
from zenif.cli import CLI, Prompt

cli = CLI(name="prompts-demo")

@cli.command
def collect_info():
    """Collect user information interactively"""
    name = Prompt.text("Enter your name").ask()
    age = Prompt.number("Enter your age").ask()
    confirmed = Prompt.confirm("Is the information correct?").ask()

    return f"Name: {name}, Age: {age}, Confirmed: {confirmed}"

if __name__ == '__main__':
    cli.run()
```

### Types of Prompts

- `Prompt.text()`: For text input (works with String schema fields)
- `Prompt.password()`: For hidden password input (works with String schema fields)
- `Prompt.confirm()`: For yes/no questions (works with Boolean schema fields)
- `Prompt.choice()`: For selecting one item from a list (works _only_ with String schema fields)
- `Prompt.checkbox()`: For selecting multiple items from a list (works with List schema fields)
- `Prompt.number()`: For numeric input (works with Integer or Float schema fields)
- `Prompt.date()`: For dates (works with String schema fields)

Find more about different types of prompts and how they work, check out [More About Prompts](../extra/more-about-prompts.md)

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
    interests = Prompt.checkbox("Select your interests",
                                choices=["Reading", "Gaming", "Sports", "Cooking", "Travel"],
                                schema=user_schema,
                                id="interests").ask()

    return f"Name: {name}, Age: {age}, Interests: {interests}"

if __name__ == '__main__':
    cli.run()
```

When using schemas with the CLI module, make sure that your `Schema` arguments match the `id` argument passed into the `Prompt` method.

When using prompts with schemas:

- The schema validates the input in real-time, providing immediate feedback to the user.
- Users cannot proceed until they provide valid input according to the schema.
- Error messages from the schema validation are displayed inline to the right of the user's cursor.

For more detailed information on creating and using schemas, please refer to the [schema documentation](schema.md).

## Special Callback Decorators

Zenif’s CLI now supports additional callback decorators that allow you to define special behaviors in your CLI:

- Root Callback (`@cli.root`):
  Runs when no subcommand is passed to the CLI. If this callback returns a value, it is logged to the terminal.
- Before Command Callback (`@cli.before`):
  Runs just before a subcommand is executed. The callback receives the subcommand name and its arguments, and any returned value is logged.
- Help Callback (`@cli.help`):
  Runs whenever help is shown—whether the user explicitly passes `-h/--help` or an unknown command is invoked. Its return value is logged as well.

Below is an example demonstrating these new additions:

```python
from zenif.cli import CLI, req, opt

cli = CLI(name="demo")

@cli.root
def root():
    return "No subcommand provided. Displaying help..." # This return value is logged.

@cli.before
def before_command(cmd_name, args):
    return f"About to execute command '{cmd_name}' with arguments: {args}" # Logged before the command runs.

@cli.help
def on_help():
    return "Help is being shown." # This is logged when help is triggered.

@cli.command
@req("name", help="Name to greet")
@opt("--greeting", default="Hello", help="Greeting to use")
@opt("--shout", is_flag=True, help="Print in uppercase")
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message # The result is logged after command execution.

if __name__ == '__main__':
    cli.run()
```
