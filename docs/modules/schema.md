# Schema Module

The Zenif Schema module provides a powerful and flexible way to define data structures and validate input. It allows you to create schemas for your data, validate inputs against these schemas, and integrate with other Zenif modules for robust data handling.

## Basic Usage

Here's a simple example of how to create and use a schema:

```python
from zenif.schema import Schema, StringF, IntegerF, ListF, Length, Value

user_schema = Schema(
    name=StringF().name("name").has(Length(min=3, max=50)),
    age=IntegerF().name("age").has(Value(min=18, max=120)),
    interests=ListF().name("interests").item_type(StringF()).has(Length(min=1))
)

# Validating data
valid_data = {
    'name': 'John Doe',
    'age': 30,
    'interests': ['coding', 'reading']
}

is_valid, errors, coerced_data = user_schema.validate(valid_data)
print(is_valid)  # True

invalid_data = {
    'name': 'Jo',
    'age': 15,
    'interests': []
}

is_valid, errors, coerced_data = user_schema.validate(invalid_data)
print(is_valid)  # False
print(errors)  # Dictionary of validation errors
```

## Available Field Types

- `StringF`: For text data
- `IntegerF`: For whole numbers
- `FloatF`: For decimal numbers
- `BooleanF`: For true/false values
- `ListF`: For lists of items
- `DictF`: For nested structures
- `DateF`: For date/time values
- `EnumF`: For enumerated values

## Validators

Validators are used to apply specific rules to fields. Zenif's built-in validators include:

- `Length(min = -inf, max = inf)`: Ensures a minimum and maximum length for strings or lists
- `Value(min = -inf, max = inf)`: Ensures a minimum and maximum value for numbers
- `Regex(pattern)`: Validates strings against a regular expression
- `EmailValidator()`: Validates email adresses

You can also create custom validators by extending the `Validator` class:

```python
from zenif.schema import Validator

class OddOrEven(Validator):
    def __init__(self, parity: str = "even"):
        self.parity = 1 if parity.lower() == "odd" else 0

    def validate(self, value):
        if value % 2 != self.parity:
            raise ValueError(f"Must be an {'even' if self.parity == 0 else 'odd'} number.")

age_schema = Schema(
    age=IntegerF().name("age").has(OddOrEven(parity="even"))
)
```

## Integration with CLI Module

The Schema module integrates seamlessly with Zenif's CLI module, allowing for robust input validation in interactive prompts. You must use the `all_optional()` method since each value is inputted one-by-one, but all prompts are still required unless a default value is provided:

```python
from zenif.cli import Prompt
from zenif.schema import Schema, StringF, IntegerF, Length, Value

user_schema = Schema(
    name=StringF().name("name").has(Length(min=3, max=50)),
    age=IntegerF().name("age").has(Value(min=18, max=120))
)

name = Prompt.text("Enter your name", schema=user_schema, id="name").ask()
age = Prompt.number("Enter your age", schema=user_schema, id="age").ask()

print(f"Name: {name}")
print(f"Age: {age}")
```

In this example, the prompts will enforce the schema rules, ensuring that the name is between 3 and 50 characters, and the age is between 18 and 120.

## Advanced Usage

### Nested Schemas

You can create nested structures using the `DictF` field type:

```python
from zenif.schema import Schema, StringF, DictF, Regex

address_schema = Schema(
    street=StringF().name("street"),
    city=StringF().name("city"),
    zipcode=StringF().name("zipcode").has(Regex(r'^\d{5}$'))
)

user_schema = Schema(
    name=StringF().name("name"),
    address=DictF().name("address").value_type(address_schema)
)
```

### List Validation

You can validate lists of items:

```python
tags_schema = Schema(
    tags=ListF().name("tags").item_type(StringF()).has(Length(min=3))
)
```

This schema ensures that 'tags' is a list of strings with at least 3 items.

### Optional Fields and Default Values

You can make fields optional or provide default values:

```python
user_schema = Schema(
    name=StringF().name("name"),
    age=IntegerF().name("age").optional(),
    is_active=BooleanF().name("is_active").default(True)
)
```

### Enum Fields

You can use enumerated values:

```python
from enum import Enum

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

user_schema = Schema(
    name=StringF().name("name"),
    role=EnumF().name("role").enum_class(UserRole).default(UserRole.USER)
)
```

## Error Handling

When validation fails, the `validate` method returns a tuple `(is_valid, errors, coerced_data)`:

- `is_valid`: A boolean indicating whether the validation passed.
- `errors`: A dictionary containing detailed error messages for each invalid field.
- `coerced_data`: A dictionary containing the validated and coerced data.

## Coercion

By default, the Schema module attempts to coerce input data to the correct types. You can disable this behavior by setting the schema to strict mode:

```python
is_valid, errors, coerced_data = user_schema.strict().validate(data)
```

In strict mode, type mismatches will result in validation errors instead of attempting coercion.

By using the Zenif Schema module, you can ensure data integrity, provide clear feedback on invalid inputs, and create more robust applications. The integration with other Zenif modules, particularly the CLI module, allows for powerful and user-friendly command-line interfaces with built-in data validation.
