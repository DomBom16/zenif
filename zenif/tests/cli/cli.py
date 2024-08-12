from zenif.cli import CLI, arg, kwarg, Prompt, install_setup_command
from zenif.schema import Schema, StringF, IntegerF, ListF, Length, Value, EmailValidator
import os

cli = CLI()

install_setup_command(cli, os.path.abspath(__file__))


@cli.command
@arg("name", help="Name to greet")
@kwarg("--greeting", default="Hello", help="Greeting to use")
@kwarg("--shout", is_flag=True, help="Print in uppercase")
def greet(name: str, greeting: str, shout: bool = False):
    """Greet a person."""
    message = f"{greeting}, {name}!"
    if shout:
        message = message.upper()
    return message


@cli.command
def test_prompts():
    """Test all available prompts"""

    class OddOrEven:
        def __init__(self, parity: str = "even"):
            self.parity = 1 if parity == "odd" else 0

        def __call__(self, value):
            if value % 2 != self.parity:
                raise ValueError(
                    f"Must be an {'even' if self.parity == 0 else 'odd'} number."
                )

    schema = Schema(
        name=StringF().name("name").has(Length(min=3, max=50)),
        age=IntegerF()
        .name("age")
        .has(Value(min=18, max=120))
        .has(OddOrEven(parity="odd")),
        interests=ListF().name("interests").item_type(StringF()).has(Length(min=3)),
        fav_interest=StringF().name("fav_interest"),
        email=StringF().name("email").has(EmailValidator()),
    ).all_optional()

    name = Prompt.text("Enter your name", schema=schema, id="name").ask()
    age = Prompt.number("Enter your age", schema=schema, id="age").ask()
    interests = Prompt.checkbox(
        "Select your interests",
        choices=["Reading", "Gaming", "Sports", "Cooking", "Travel"],
        schema=schema,
        id="interests",
    ).ask()
    fav_interest = Prompt.choice(
        "Select your favorite interest",
        choices=interests,
        schema=schema,
        id="fav_interest",
    ).ask()
    email = Prompt.text("Enter your email", schema=schema, id="email").ask()

    print(f"Name: {name}")
    print(f"Age: {age}")
    print(f"Interests: {', '.join(interests)}")
    print(f"Favorite Interest: {fav_interest}")
    print(f"Email: {email}")


if __name__ == "__main__":
    cli.run()
