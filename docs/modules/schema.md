# Schema Module

The Zenif Schema module provides a powerful and flexible way to define data structures and validate input. It allows you to create schemas for your data, validate inputs against these schemas, and integrate with other Zenif modules for robust data handling.

## Table of Contents

- [Schema Module](#schema-module)
  - [Table of Contents](#table-of-contents)
  - [Basic Usage](#basic-usage)
  - [Available Field Types](#available-field-types)
  - [Validators](#validators)
  - [Integration with CLI Module](#integration-with-cli-module)
  - [More Usage](#more-usage)
    - [List Validation](#list-validation)
    - [Optional Fields and Default Values](#optional-fields-and-default-values)
    - [Enum Fields](#enum-fields)
  - [Error Handling](#error-handling)
  - [Coercion](#coercion)

## Basic Usage

Here's a simple example of how to create and use a schema:

```python
from zenif.schema import Schema, StringF, IntegerF, ListF, Length, Value

user_schema = Schema({
    "name": StringF().has(Length(min=3, max=50)),
    "age": IntegerF().has(Value(min=18, max=120)),
    "interests": ListF().items(StringF()).has(Length(min=1))
})

# Validating data
valid_data = {
    'name': 'John Doe',
    'age': 30,
    'interests': ['coding', 'reading']
}

is_valid, errors, coerced_data = user_schema.validate(valid_data)
print(is_valid)
# True
print(errors)
# {}

invalid_data = {
    'name': 'Jo',
    'age': 246,
    'interests': []
}

is_valid, errors, coerced_data = user_schema.validate(invalid_data)
print(is_valid)
# False
print(errors)
# {'name': [('LengthError', 'Minimum length is 3.')], 'age': [('ValueRangeError', 'Maximum value is 120.')], 'interests': [('LengthError', 'Minimum length is 1.')]}
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

Although you should avoid it, if you ever need to create a new field type, simply extend the SchemaField class:

```python
from zenif.schema import SchemaField

class MyTypeF(SchemaField[MyType]):
    ...

    def coerce(self, value: any) -> MyType:
        return ...
```

When creating a field, your class name should be in the `{type}F` format, where the type name is followed by the letter "F".

## Validators

Validators are used to apply specific rules to fields. Zenif's built-in validators include:

- `Length(min=None, max=None)`: Ensures a minimum and maximum length for strings or lists
- `Value(min=None, max=None)`: Ensures a minimum and maximum value for numbers
- `Regex(pattern)`: Validates strings against a regular expression
- `Email()`: Validates email addresses
- `Date()`: Ensures the field is in the format YYYY-MM-DD
- `Alphanumeric()`: Ensures the field only contains letters and numbers
- `URL()`: Validates URL addresses
- `NotEmpty()`: Ensures the field is not empty
- `Truthy()`: Ensures a value is truthy
- `Falsy()`: Ensures a value is falsy

You can also create custom validators by extending the base `Validator` class. **Important:** When your custom validator extends the `Validator` class, its `__call__` method automatically wraps any exceptions thrown in the `_validate` method. This ensures that any error raised is an instance of `ValidationError` or one of its subclasses, which maintains consistent error handling across the schema. For example:

```python
from zenif.schema import Validator

class OddOrEven(Validator):
    def __init__(self, parity: str = "even", err: str | None = None):
        super().__init__(err)
        self.parity = 1 if parity.lower() == "odd" else 0

    def _validate(self, value):
        if value % 2 != self.parity:
            # Even if a different type of error is raised, the base Validator wraps it as a ValidationError
            raise ValueError(f"Must be an {'even' if self.parity == 0 else 'odd'} number.")
```

In addition, the framework now provides more specific exceptions that extend `ValidationError`, such as:

- `LengthError`
- `ValueRangeError`
- `RegexError`
- `EmailError`
- `AlphanumericError`
- `URLError`
- `DateError`
- `EmptyValueError`
- `NotTruthyError`
- `NotFalsyError`

These exceptions allow for more granular error handling and clearer messages.

## Integration with CLI Module

The Schema module integrates seamlessly with Zenif's CLI module, allowing for robust input validation in interactive prompts.

```python
from zenif.cli import Prompt
from zenif.schema import Schema, StringF, IntegerF, Length, Value

user_schema = Schema({
    "name": StringF().has(Length(min=3, max=50)),
    "age": IntegerF().has(Value(min=18, max=120))
})

name = Prompt.text("Enter your name", schema=user_schema, id="name").ask()
age = Prompt.number("Enter your age", schema=user_schema, id="age").ask()

print(f"Name: {name}")
print(f"Age: {age}")
```

In this example, the prompts will enforce the schema rules, ensuring that the name is between 3 and 50 characters, and the age is between 18 and 120.

## More Usage

### List Validation

You can validate lists of items:

```python
tags_schema = Schema({ "tags": ListF().items(StringF()).has(Length(min=3)) })
```

This schema ensures that 'tags' is a list of strings with at least 3 items.

### Optional Fields and Default Values

You can make fields optional or provide default values:

```python
user_schema = Schema(
    name=StringF().name("name"),
    age=IntegerF().name("age").default(),
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
    role=EnumF().name("role").enum(UserRole).default(UserRole.USER)
)
```

## Error Handling

When validation fails, the `validate` method returns a tuple `(is_valid, errors, coerced_data)`:

- **`is_valid`**: A boolean indicating whether the validation passed.
- **`errors`**: A dictionary containing detailed error messages for each invalid field. Errors are now returned as tuples in the form `(ErrorClass, message)`, ensuring that you can programmatically distinguish between different types of validation errors.
- **`coerced_data`**: A dictionary containing the validated and coerced data.

For example, if a field fails a length check, the error might look like `('LengthError', 'Minimum length is 3')`.

## Coercion

By default, the Schema module attempts to coerce input data to the correct types. You can disable this behavior by setting the schema to strict mode:

```python
is_valid, errors, coerced_data = user_schema.strict().validate(data)
```

In strict mode, type mismatches will result in validation errors instead of attempting coercion.
