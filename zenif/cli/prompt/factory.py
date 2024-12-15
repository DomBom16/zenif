from zenif.schema import Schema

from .prompts.text import TextPrompt
from .prompts.password import PasswordPrompt
from .prompts.confirm import ConfirmPrompt
from .prompts.choice import ChoicePrompt
from .prompts.checkbox import CheckboxPrompt
from .prompts.number import NumberPrompt
from .prompts.date import DatePrompt
from .prompts.editor import EditorPrompt

class Prompt:
    """A class for prompting the user for input."""

    @staticmethod
    def text(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> TextPrompt:
        """Creates a text prompt where the user can input a text string."""
        return TextPrompt(message, schema, id)

    @staticmethod
    def password(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> PasswordPrompt:
        """Creates a password prompt where the user can input a text string masked with '*'."""
        return PasswordPrompt(message, schema, id)

    @staticmethod
    def confirm(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> ConfirmPrompt:
        """Creates a confirm prompt where the user can confirm an action, either yes or no."""
        return ConfirmPrompt(message, schema, id)

    @staticmethod
    def choice(
        message: str,
        choices: list[str],
        schema: Schema | None = None,
        id: str | None = None,
    ) -> ChoicePrompt:
        """Creates a choice prompt where the user can select from a list of choices."""
        return ChoicePrompt(message, choices, schema, id)

    @staticmethod
    def checkbox(
        message: str,
        choices: list[str],
        schema: Schema | None = None,
        id: str | None = None,
    ) -> CheckboxPrompt:
        """Creates a checkbox prompt where the user can select multiple choices from a list of choices."""
        return CheckboxPrompt(message, choices, schema, id)

    @staticmethod
    def number(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> NumberPrompt:
        """Creates a number prompt where the user can input a number."""
        return NumberPrompt(message, schema, id)

    @staticmethod
    def date(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> DatePrompt:
        """Creates a date prompt where the user can input a date."""
        return DatePrompt(message, schema, id)

    @staticmethod
    def editor(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> EditorPrompt:
        """Creates an editor prompt where the user can input multiple lines of text, along with syntax highlighting if specified."""
        return EditorPrompt(message, schema, id)
