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

The CLI module comes with a handy method that let's your users install the given file as a command. By importing and running the `install_setup_command()` method, your users can run `python yourfile.py setup --alias youralias` to simplify the command line interaction.

```python
from zenif.cli import CLI, install_setup_command
import os

cli = CLI()

# Under the hood, the install_setup_command method creates an
# @cli.command decorated function that runs a shell script.
install_setup_command(cli=cli, script_path=os.path.abspath(__file__))
```

## Interactive Prompts with Schema Validation

The CLI module is now able to be integrated with the Schema module to validate your inputs in real-time:

```python
from zenif.cli import CLI, Prompt, schemafy
from zenif.schema import Schema, StringF, IntegerF, ListF, Length, Value

cli = CLI()

user_schema = Schema({
    name=StringF()
         .name("name")
         .has(Length(min=3, max=50)),
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
})

@cli.command
def setup():
    """Interactive setup command with schema validation"""
    name = Prompt.text("Enter your name", schema=user_schema, id="name").ask()
    age = Prompt.number("Enter your age", schema=user_schema, id="age").ask()
    # By defining .commas() the input will visually show commas but the
    # returned value will not include commas. This is useful for inputs
    # that usually include values that are harder to read without commas.
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

When using schemas with the CLI module, make sure that your keys are kebab_cased versions of your prompts (e.g., `"Enter your name"` -> `"enter_your_name"`).

## Available Prompt Types

- `Prompt.text()`: For text input (works with String schema fields)
- `Prompt.password()`: For hidden password input (works with String schema fields)
- `Prompt.confirm()`: For yes/no questions (works with Boolean schema fields)
- `Prompt.choice()`: For selecting one item from a list (works only with String schema fields)
- `Prompt.checkbox()`: For selecting multiple items from a list (works with List schema fields)
- `Prompt.number()`: For numeric input (works with Integer or Float schema fields)

Each prompt type now supports schema validation when a schema is provided.

## Type Checking for ChoicePrompt

The `ChoicePrompt` (used by `Prompt.choice()`) now includes type checking to ensure it's only used with String schema fields. If a non-String field is provided, a TypeError will be raised with a clear error message.

## Schema Integration

When using prompts with schemas:

- The schema validates the input in real-time, providing immediate feedback to the user.
- Users cannot proceed until they provide valid input according to the schema.
- Error messages from the schema validation are displayed inline to the right of the users cursor.

For more detailed information on creating and using schemas, please refer to the `schema.md` documentation.

By using these features of the Zenif CLI module, you can create command-line applications with intuitive argument parsing, interactive prompts, and robust input validation. This allows for more user-friendly, flexible, and reliable command-line interfaces in your Python projects.
