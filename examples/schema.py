from datetime import datetime

from zenif.schema import (
    BooleanF,
    Email,
    IntegerF,
    Length,
    Regex,
    Schema,
    StringF,
    Value,
)

user_schema = Schema(
    {
        "username": (
            StringF()
            .pre(lambda x: x.strip().lower())
            .has(Length(min=3, max=20))
            .post(lambda x: x if x.startswith("@") else f"@{x}")
        ),
        "email": (
            StringF()
            .pre(lambda x: x.strip().lower())
            .has(Email())
            .default("user@example.com")
        ),
        "age": IntegerF().has(Value(min=0, max=120)).default(18),
        "is_premium": BooleanF().default(False),
        "premium_code": (
            StringF()
            .pre(lambda x: x.strip().lower().replace("-", ""))
            .when(
                lambda data: data.get("is_premium", False),
                "Premium code required for premium users",
            )
            .default("")
            .has(Regex(r"^[a-z]{4}[a-z]{4}[a-z]{4}$", err="Invalid format."))
        ),
        "created_at": IntegerF().default(lambda: int(datetime.now().timestamp())),
    }
)

# Validate data
data = {
    "username": "  JohnDoe  ",
    "email": "  JOHN@EXAMPLE.COM  ",
    "age": 25,
    "is_premium": True,
    "premium_code": "JGUI-PYBF-WSMN",
}

is_valid, errors, coerced_data = user_schema.validate(data)
print(coerced_data)
# Output: {
#     'username': '@johndoe',
#     'email': 'john@example.com',
#     'age': 25,
#     'is_premium': True,
#     'premium_code': "jguipybfwsmn",
#     'created_at': 1640995200
# }
