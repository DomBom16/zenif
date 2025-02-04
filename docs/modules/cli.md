# CLI Module

Zenif includes a CLI (Command Line Interface) module that allows you to easily create interactive command-line applications. This module provides tools for building CLIs with argument parsing, command management, and now includes schema integration for robust input validation, as well as tooling for interactive prompts in the terminal.

## Table of Contents

- [CLI Module](#cli-module)
  - [Table of Contents](#table-of-contents)
  - [Applets](#applets)
    - [Getting Started with Applets](#getting-started-with-applets)
    - [Setting Up ZSH Commands for Your Users](#setting-up-zsh-commands-for-your-users)
    - [Special Callback Decorators](#special-callback-decorators)
  - [Prompts](#prompts)
    - [Getting Started With Prompts](#getting-started-with-prompts)
    - [Types of Prompts](#types-of-prompts)
  - [Interactive Prompts with Schema Validation](#interactive-prompts-with-schema-validation)

## Applets

Within the CLI module, the Applets submodule is designed to facilitate the creation of lightweight yet functional CLI applications. These applications can be executed directly from the command line, providing a streamlined way to interact with the system or perform specific tasks.

### Getting Started with Applets

Here's a comprehensive example of how to create a CLI application using Zenif, demonstrating the basic capabilites of Zenif's CLI applets.

First, import the required modules from the Zenif library and initialize an instance.

```py
from zenif.cli import CLI

cli = CLI(name="applets-demo")
```

The `CLI` class is a command-line interface (CLI) framework for defining and executing commands, providing functionality to register commands, set callbacks, and handle command-line arguments.

Register a function as a command within the CLI using the `@cli.command` decorator. This tells Zenif that the function below will be a CLI command. In this case, the function name greet becomes the command name that users will invoke.

```py
@cli.command()
def greet():
    ...
```

Use `@cli.arg` to define a required positional arguments that the user must provide.

```python
@cli.arg("name", help="Name to greet")
```

Here, `"name"` is the required argument, meaning the user must enter a name when running the command. The help argument provides useful insight to the user when they run `applets-demo greet --help`

Similarly, we can use `@cli.opt` to define an option, an optional argument that accepts a value.

```python
@cli.opt("greeting", default="Hello", help="Greeting to use")
```

This optional argument `--greeting` allows the user to specify a custom greeting. If no greeting is provided, it defaults to `"Hello"`.

While `@cli.opt` can be great for optional values, `@cli.flag` can be extremely useful in providing boolean switches. Unlike regular options, this flag does not require a value. If `--shout` is included in the command, its value is `True`; otherwise, it remains `False`.

```python
@cli.flag("shout", help="Print in uppercase")
```

Unlike regular options, this flag does not require a value. If `--shout` is included in the command, its value is `True`; otherwise, it remains `False`.

While this is all well and nifty, typing commands over and over can get pretty tedious. We can help mitigate this by using `@cli.alias` to define parameter shortands.

```python
@cli.alias("greeting", "g")
@cli.alias("shout", "s")
```

Instead of using `--greeting` and `--shout`, we can now simply use `-g` and `-s`. Much faster to type.

Now, implement the actual function that processes user input.

```python
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message # This will be printed to the terminal
```

Docstrings used in your commands are used as help descriptions.

Unfortuneately, we can't run this script just yet since our function isn't being called anywhere. In order to call this from the command line, we need to pass the `cli.run()` method to activate the CLI.

```python
if __name__ == "__main__":
    cli.run()
```

So far, our users can interact with the `greet` command like so:

```bash
python script.py greet Alice
# Hello, Alice!
python script.py greet Alice --greeting "Hi" -s
# HI, ALICE!
python script.py greet "Super Bob" --shout
# HELLO, SUPER BOB!
```

However, using a subcommand name can sometimes be redundant. To fix this, we can employ the `@cli.root` decorator and the `cli.execute()` method.

`@cli.root` is one of the [three special callback decorators](#special-callback-decorators) that can help make workflows with the CLI module easier. If you want the `CLI` to run a default command when no subcommand is provided, use the `@cli.root` decorator. This function is executed when the script is run without a subcommand:

```python
@cli.root
def root():
    # Programatically runs 'greet "Alice" --greeting "Hi"'
    cli.execute("greet", ["Alice", "--greeting", "Hi"])
```

Now when we run the script by itself, we still get an output:

```bash
python script.py
# Hi, Alice!
```

Here's the code put together.

```python
from zenif.cli import CLI

cli = CLI(name="demo")

@cli.command
@cli.arg("name", help="Name to greet")
@cli.opt("greeting", default="Hello", help="Greeting to use")
@cli.flag("shout", help="Print in uppercase")
@cli.alias("greeting", "g")
@cli.alias("shout", "s")
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message

@cli.root
def root():
    # Programmatically execute the 'greet' command.
    cli.execute("greet", ["Alice", "--greeting", "Hi"])

if __name__ == '__main__':
    cli.run()
```

### Setting Up ZSH Commands for Your Users

The CLI module comes with a handy method that let's your users install the given file as a .zshrc function. By running the `install_setup()` method, your users can create an alias in their `~/.zshrc` configuration.

```python
from zenif.cli import CLI, install_setup
import os

cli = CLI()
install_setup(cli=cli, script_path=os.path.abspath(__file__))
```

Users can now run `python yourfile.py setup --alias youralias` so insteand of running `python yourfile.py` they can run `youralias`.

### Special Callback Decorators

Zenif’s CLI now supports additional callback decorators that allow you to define special behaviors in your CLI:

- Root Callback (`@cli.root`)
  Runs when no subcommand is passed. If the callback returns a value, it is logged to the terminal.
- Before Command Callback (`@cli.before`)
  Runs just before a subcommand is executed. It receives the subcommand name and its arguments; any returned value is logged.
- Help Callback (`@cli.help`)
  Runs whenever help is shown. Its return value is logged as well.

Below is an example demonstrating these new additions:

```python
from zenif.cli import CLI

cli = CLI()

@cli.root
def root():
    return "No subcommand provided. Displaying help..." # This return value is logged.

@cli.before
def before_command(cmd: str, args: list[str]):
    return f"About to execute command '{cmd}' with arguments: {args}" # Logged before the command runs.

@cli.help
def on_help():
    return "Help is being shown." # This is logged when help is triggered.

if __name__ == '__main__':
    cli.run()
```

## Prompts

Zenif's CLI module also provides a flexible prompting system for interactive CLI applications. Prompts let you collect user input dynamically with built-in validation and beautiful output formatting.

### Getting Started With Prompts

To use prompts in your CLI application, import the `Prompt` class and set up a CLI command [like we did earlier](#getting-started-with-applets):

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
