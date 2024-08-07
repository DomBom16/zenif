# CLI Module

FluxUtils includes a CLI (Command Line Interface) module that allows you to easily create interactive command-line applications. This module provides tools for building CLIs with argument parsing and command management.

## Basic Usage

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

### How It Works

In this example:

- We create a `CLI` instance.
- We define a `greet` command using the `@cli.command` decorator.
- We add a required `name` argument using the `@argument` decorator. This is a positional argument.
- We add an optional `--greeting` option using the `@option` decorator. This option has a default value of "Hello".
- We add an optional `--shout` flag using the `@option` decorator. This is a boolean flag.
- The `greet` function contains the logic for the command.
- We call `cli.run()` to start the CLI application. You can run the application multiple times if you wish to.

### Running Your Application

You can run your application however you've defined your commands, arguments, and options. In this example, some possible combinations include the following:

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

### Key Points

1. `@argument` is used for required positional arguments. In this case, `name` must always be provided.
2. `@option` is used to define command-line options. These are typically optional and are prefixed with `--` (or `-` for short versions).
   - The `--greeting` option is optional and has a default value.
   - The `--shout` option is a flag (boolean) that doesn't require a value.
3. Options defined with `@option` can be required or optional, depending on how you configure them. In this example, both are optional.

This structure allows for flexible and intuitive command-line interfaces, where users can provide required arguments and optionally customize behavior with additional options.

## Interactive Prompts

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

## Available Prompt Types

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
