class AppletError(Exception):
    """Base exception for Applet-related errors."""

    pass


class AppletParseError(AppletError):
    """Raised when there's an error parsing command arguments."""

    pass


class AppletCommandError(AppletError):
    """Raised when a command execution fails."""

    pass


class AppletHelpError(AppletError):
    """Raised when help is requested."""

    pass


class AppletConfigError(AppletError):
    """Raised when there's an error in applet configuration."""

    pass


class AppletNotFoundError(AppletError):
    """Raised when a requested command or parameter is not found."""

    pass


class AppletValidationError(AppletError):
    """Raised when command arguments validation fails."""

    pass
