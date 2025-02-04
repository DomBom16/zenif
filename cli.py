#!/usr/bin/env python3
from zenif.cli import Applet, Prompt as p
from zenif.schema import (
    Schema,
    BooleanF,
    StringF,
    IntegerF,
    ListF,
    Length,
    Value,
    Email,
    NotEmpty,
)
import os

a = Applet()

a.install(os.path.abspath(__file__))


@a.command
@a.arg("branch", help="The branch to fetch")
@a.opt("depth", default=10, help="The depth to use")
@a.alias("depth", "d")
def fetch(branch, depth):
    """
    Fetch a branch with a specified depth.

    Usage examples:
      fetch main --depth=10
      fetch feature -d=10
    """
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


@a.command
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
        are_you_sure=BooleanF().name("continue"),
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

    for i in range(4):
        print(i + 1)

    p.keypress("Press a, b, or c").keys("a", "b", "c").ask()

    if (
        not p.confirm("Are you sure you want to continue?", schema, "are_you_sure")
        .default(True)
        .ask()
    ):
        return
    # name = p.text("Enter your name", schema, "name").ask()
    # email = p.text("Enter your email", schema, "email").ask()
    # password = p.password("Enter your password", schema, "password").peeper().ask()
    # date = p.date("Enter your date of birth").month_first().show_words().ask()
    # age = p.number("Enter your age", schema, "age").ask()
    editor = p.editor("Enter your hacker code").language("py").ask()
    interests = p.checkbox(
        "Select your interests",
        ["Reading", "Gaming", "Sports", "Cooking", "Travel"],
        schema,
        "interests",
    ).ask()
    fav_interest = p.choice(
        "Select your favorite interest",
        interests,
        schema,
        "fav_interest",
    ).ask()

    # print(f"{name=}")
    # print(f"{email=}")
    # print(f"{password=}")
    # print(f"{date=}")
    # print(f"{age=}")
    print(f"{editor=}")
    print(f"{interests=}")
    print(f"{fav_interest=}")


@a.root
def root():
    a.execute("test_prompts")


@a.help
def help():
    # return "This is the help command"
    pass


@a.before
def before(command: str, args: list[str]):
    # return f"Command: {command}, Args: {args}"
    pass


if __name__ == "__main__":
    a.run()
