from zenif.cli import CLI, arg, kwarg, Prompt, install_setup_command
from zenif.schema import Schema, StringF, IntegerF, ListF, Length, Value, Email, NotEmpty
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
                    f"Must be an {'even' if self.parity ==
                                  0 else 'odd'} number."
                )
            
    # clear the screen
    os.system("cls" if os.name == "nt" else "clear")

    schema = Schema(
        name=StringF().name("name").has(Length(min=3, max=50)),
        password=StringF().name("password").has(NotEmpty()),
        age=IntegerF()
        .name("age")
        .has(Value(min=18, max=120))
        .has(OddOrEven(parity="odd")),
        interests=ListF()
        .name("interests")
        .item_type(StringF())
        .has(Length(min=3, err="Select a minimum of 3 interests.")),
        fav_interest=StringF().name("fav_interest"),
        email=StringF().name("email").has(Email()),
    ).all_optional()

    name = Prompt.text("Enter your name", schema, "name").ask()
    password = Prompt.password("Enter your password", schema, "password").peeper().ask()
    age = Prompt.number("Enter your age", schema, "age").ask()
    interests = Prompt.checkbox(
        "Select your interests",
        ["Reading", "Gaming", "Sports", "Cooking", "Travel"],
        schema,
        "interests",
    ).ask()
    fav_interest = Prompt.choice(
        "Select your favorite interest",
        interests,
        schema,
        "fav_interest",
    ).ask()
    email = Prompt.text("Enter your email", schema, "email").ask()

    print(f"{name=}")
    print(f"{password=}")
    print(f"{age=}")
    print(f"{interests=}")
    print(f"{fav_interest=}")
    print(f"{email=}")


if __name__ == "__main__":
    cli.run()
