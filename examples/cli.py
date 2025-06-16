#!/usr/bin/env python3
import os
import time

from zenif.cli import Applet
from zenif.cli import Prompt as p
from zenif.constants import Cursor
from zenif.log import Logger
from zenif.schema import (
    BooleanF,
    DateF,
    Email,
    IntegerF,
    Length,
    ListF,
    NotEmpty,
    Regex,
    Schema,
    StringF,
    ValidationError,
    Validator,
    Value,
)

L = Logger({"log_line": {"format": "simple"}})


a = Applet()

a.install(os.path.abspath(__file__))


# @a.root
@a.command(aliases=["f"])
@a.arg("branch", help="The branch to fetch")
@a.opt("depth", default=10, help="The depth to use")
@a.alias("depth", "d")
def fetch(branch: str, depth: int):
    """
    Fetch a branch with a specified depth.

    Usage examples:
      fetch main --depth=10
      fetch feature -d=10
    """
    time.sleep(2)
    return f"Fetching branch '{branch}' with depth={depth}"


@a.command
@a.arg("path", help="The folder path")
@a.flag("all", help="Show all")
def ls(path, all):
    """
    List directory contents.

    Usage example: ls /my-path --all
    """
    return f"Listing {path} with all={all}"


@a.root
@a.command(aliases=["tp"])
def test_prompts():
    """Test all available prompts"""

    class OddOrEven(Validator):
        def __init__(self, parity: str = "even", err: str | None = None):
            super().__init__(err)
            self.parity = "odd" if parity == "odd" else "even"
            self.parity_mod = 1 if parity == "odd" else 0

        def validate(self, value):
            if value % 2 != self.parity_mod:
                raise ValidationError(f"Must be an {self.parity} number.")

    # clear the screen
    os.system("cls" if os.name == "nt" else "clear")

    s = Schema(
        {
            "are_you_sure": BooleanF(),
            "name": StringF().has(Length(min=3, max=50)),
            "email": StringF().has(Email()),
            "password": StringF()
            .has(Length(min=8))
            .has(
                Regex(
                    r"^(?=.*[a-z]).+$",
                    err="Password must contain at least one lowercase letter.",
                )
            )
            .has(
                Regex(
                    r"^(?=.*[A-Z]).+$",
                    err="Password must contain at least one uppercase letter.",
                )
            )
            .has(
                Regex(r"^(?=.*\d).+$", err="Password must contain at least one digit.")
            )
            .has(
                Regex(
                    r"^(?=.*[@$!%*#?&]).+$",
                    err="Password must contain at least one special character.",
                )
            ),
            "date": DateF().has(NotEmpty()),
            "salary": IntegerF().has(Value(min=0, max=1000000)),
            "age": IntegerF().has(Value(min=18, max=120)).has(OddOrEven(parity="odd")),
            "editor": StringF().has(NotEmpty()),
            "interests": ListF()
            .items(StringF())
            .has(Length(min=3, err="Select a minimum of 3 interests.")),
            "fav_interest": StringF(),
        }
    )

    for i in range(4):
        print(i + 1)

    print(Cursor.get())

    p.keypress("Press a, b, or c").keys("a", "b", "c").ask()

    if (
        not p.confirm("Are you sure you want to continue?", s, "are_you_sure")
        .default(True)
        .ask()
    ):
        return
    name = p.text("Enter your name", s, "name").ask()
    email = p.text("Enter your email", s, "email").ask()
    password = p.password("Enter your password", s, "password").peeper().ask()
    date = (
        p.date("Enter your date of birth", s, "date").month_first().show_words().ask()
    )
    salary = p.number("Enter your salary", s, "salary").commas().ask()
    age = p.number("Enter your age", s, "age").ask()
    editor = p.editor("Enter your hacker code", s, "editor").language("py").ask()
    interests = (
        p.checkbox("Select your interests", s, "interests")
        .choices("Reading", "Gaming", "Sports", "Cooking", "Travel")
        .ask()
    )
    fav_interest = (
        p.choice("Select your favorite interest", s, "fav_interest")
        .choices(interests)
        .ask()
    )

    L.info(
        s.validate(
            {
                "are_you_sure": True,
                "name": name,
                "email": email,
                "password": password,
                "date": date,
                "salary": salary,
                "age": age,
                "editor": editor,
                "interests": interests,
                "fav_interest": fav_interest,
            }
        )
    )


@a.help
def help():
    return "Help"


@a.before
def before(command: str, args: list[str]):
    return (command, args)


@a.after
def after(command: str, args: list[str]):
    return


if __name__ == "__main__":
    L.debug(vars(a))
    a.run()
