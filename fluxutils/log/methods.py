import inspect
import os

from .base import Logger


class Logger(Logger):
    """A class used to log messages with granular customizability.

    Args:
        rules (dict, optional): A ruleset that overrides the default rules. To view the default rules, view Logger().defaults. Defaults to {}.
    """

    def __log_method(self, values, level, sep, pretty_print) -> None:
        # Get current frame
        frame = inspect.currentframe()
        # Get the caller's frame
        caller_frame = frame.f_back.f_back

        module = caller_frame.f_globals["__name__"]
        function = caller_frame.f_code.co_name
        wrapping_func = caller_frame.f_code.co_name
        line_number = caller_frame.f_lineno
        file_name = os.path.basename(caller_frame.f_code.co_filename)

        metadata = {
            "module": module,
            "function": function,
            "wrapping_func": wrapping_func,
            "line_number": line_number,
            "file_name": file_name,
            "value_count": len(values),
        }

        self.__log(
            level=level,
            values=values,
            metadata=metadata,
            sep=sep,
            pretty_print=pretty_print,
        )

    def info(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with an "info" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["info"]["name"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def debug(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with a "debug" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["debug"]["name"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def success(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with a "success" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["success"]["name"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def warning(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with a "warning" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["warning"]["name"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def error(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with an "error" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["error"]["name"],
            sep=sep or "\n",
            pretty_print=rich,
        )

    def lethal(self, *values, sep: str = None, rich: bool = True) -> None:
        """Logs the given values to the console with a "lethal" level.

        Args:
            sep (str, optional): String inserted between values. Defaults to None
            rich (bool, optional): Format values for easier readability with syntax highlighting. Defaults to True
        """

        self.__log_method(
            values=values,
            level=self.__levels["lethal"]["name"],
            sep=sep or "\n",
            pretty_print=rich,
        )
