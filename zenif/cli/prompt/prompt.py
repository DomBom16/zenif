from ...schema import Schema
from .checkbox import CheckboxPrompt
from .choice import ChoicePrompt
from .confirm import ConfirmPrompt
from .date import DatePrompt
from .editor import EditorPrompt
from .key import KeyPrompt
from .number import NumberPrompt
from .password import PasswordPrompt
from .text import TextPrompt


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
        schema: Schema | None = None,
        id: str | None = None,
    ) -> ChoicePrompt:
        """Creates a choice prompt where the user can select from a list of choices."""
        return ChoicePrompt(message, schema, id)

    @staticmethod
    def checkbox(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> CheckboxPrompt:
        """Creates a checkbox prompt where the user can select multiple choices from a list of choices."""
        return CheckboxPrompt(message, schema, id)

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

    @staticmethod
    def keypress(
        message: str,
        schema: Schema | None = None,
        id: str | None = None,
    ) -> KeyPrompt:
        """Creates a keypress prompt where the user can input multiple keys."""
        return KeyPrompt(message, schema, id)
