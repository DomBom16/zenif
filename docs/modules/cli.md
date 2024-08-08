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

## Interactive Prompts with Schema Validation

The CLI module is now able to be integrated with the Schema module to validate your inputs in real-time:

```python
from zenif.cli import CLI, Prompt
from zenif.schema import Schema, String, Integer, List, MinLength, MaxLength, MinValue, MaxValue

cli = CLI()

user_schema = Schema({
    'enter_your_name': String(validators=[MinLength(3), MaxLength(50)]),
    'enter_your_age': Integer(validators=[MinValue(18), MaxValue(120)]),
    'select_your_interests': List(String(), validators=[MinLength(1), MaxLength(5)])
})

@cli.command
def setup():
    """Interactive setup command with schema validation"""
    name = Prompt.text("Enter your name", schema=user_schema).ask()
    age = Prompt.number("Enter your age", schema=user_schema).ask()
    interests = Prompt.checkbox("Select your interests", 
                                choices=["Reading", "Gaming", "Sports", "Cooking", "Travel"], 
                                schema=user_schema).ask()

    print(f"Name: {name}")
    print(f"Age: {age}")
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
