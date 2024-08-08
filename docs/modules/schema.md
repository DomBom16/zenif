# Schema Module

The Zenif Schema module provides a powerful and flexible way to define data structures and validate input. It allows you to create schemas for your data, validate inputs against these schemas, and integrate with other Zenif modules for robust data handling.

## Basic Usage

Here's a simple example of how to create and use a schema:

```python
from zenif.schema import Schema, String, Integer, List, MinLength, MaxLength, MinValue, MaxValue

user_schema = Schema({
    'name': String(validators=[MinLength(3), MaxLength(50)]),
    'age': Integer(validators=[MinValue(18), MaxValue(120)]),
    'interests': List(String(), validators=[MinLength(1), MaxLength(5)])
})

# Validating data
valid_data = {
    'name': 'John Doe',
    'age': 30,
    'interests': ['coding', 'reading']
}

result = user_schema.validate(valid_data)
print(result.is_valid)  # True

invalid_data = {
    'name': 'Jo',
    'age': 15,
    'interests': []
}

result = user_schema.validate(invalid_data)
print(result.is_valid)  # False
print(result.errors)  # Dictionary of validation errors
```

## Available Field Types

- `String`: For text data
- `Integer`: For whole numbers
- `Float`: For decimal numbers
- `Boolean`: For true/false values
- `List`: For lists of items
- `Dict`: For nested structures
- `Email`: For emails; complies with [RFC 5322](https://www.ietf.org/rfc/rfc5322.txt)

## Validators

Validators are used to apply specific rules to fields. Some common validators include:

- `MinLength(min_length)`: Ensures a minimum length for strings or lists
- `MaxLength(max_length)`: Ensures a maximum length for strings or lists
- `MinValue(min_value)`: Ensures a minimum value for numbers
- `MaxValue(max_value)`: Ensures a maximum value for numbers
- `Regex(pattern)`: Validates strings against a regular expression

You can also create custom validators by implementing the `__call__` method:

```python
class EvenNumber:
    def __call__(self, value):
        if value % 2 != 0:
            raise ValueError("Must be an even number.")

age_schema = Schema({
    'age': Integer(validators=[EvenNumber()])
})
```

## Integration with CLI Module

The Schema module integrates seamlessly with Zenif's CLI module, allowing for robust input validation in interactive prompts:

```python
from zenif.cli import Prompt
from zenif.schema import Schema, String, Integer

user_schema = Schema({
    'name': String(validators=[MinLength(3), MaxLength(50)]),
    'age': Integer(validators=[MinValue(18), MaxValue(120)])
})

name = Prompt.text("Enter your name", schema=user_schema).ask()
age = Prompt.number("Enter your age", schema=user_schema).ask()

print(f"Name: {name}")
print(f"Age: {age}")
```

In this example, the prompts will enforce the schema rules, ensuring that the name is between 3 and 50 characters, and the age is between 18 and 120.

## Advanced Usage

### Nested Schemas

You can create nested structures using the `Dict` field type:

```python
address_schema = Schema({
    'street': String(),
    'city': String(),
    'zipcode': String(validators=[Regex(r'^\d{5}$')])
})

user_schema = Schema({
    'name': String(),
    'address': Dict(address_schema)
})
```

### List Validation

You can validate lists of items:

```python
tags_schema = Schema({
    'tags': List(String(), validators=[MinLength(1), MaxLength(5)])
})
```

This schema ensures that 'tags' is a list of strings with at least 1 and at most 5 items.

## Error Handling

When validation fails, the `validate` method returns a `ValidationResult` object with `is_valid` set to `False` and an `errors` dictionary containing detailed error messages for each invalid field.

By using the Zenif Schema module, you can ensure data integrity, provide clear feedback on invalid inputs, and create more robust applications. The integration with other Zenif modules, particularly the CLI module, allows for powerful and user-friendly command-line interfaces with built-in data validation.
