from fluxutils.log import Logger, Ruleset

# Initialize a Logger instance
logger = Logger()

# Enable stacking
logger.ruleset.stacking.enabled = True
# Timestamps will be printed during every log
logger.ruleset.timestamps.always_show = True

# Define a specific ruleset
ruleset = Ruleset(
    {
        "timestamps": {
            "always_show": False,  # If False, only prints the time changes
            "use_utc": False,  # If True, use UTC for timestamps; otherwise, use local time
        },
        "formatting": {
            # If True, formats data structures with the Black formatter.
            "pretty_print": True,
            # Width to format syntax to. If 0, the width is set to the available space
            "fixed_format_width": 0,
        },
        "filtering": {
            "min_level": 0,  # The minimum log level to output; logs below this level are ignored. Can either be an integer, the level number, or a string, the level name
            # If a message contains any of the substrings in the list, it will not be logged
            "exclude_messages": [],
            # Only messages containing any of the substrings in the list will be logged; overridden by exclude_messages
            "include_only_messages": [],
        },
        "log_line": {"format": "filled"},
    }
)

# Add the log.log file as a file stream with specific ruleset
logger.stream.file.add("log.log", reset=True, ruleset=ruleset)


def superlongfunctionname():
    logger.error("Could", "not", "run function")


# Tests truncation of long function names
superlongfunctionname()

logger.info(logger.ruleset.dict.all)  # -> l.__rules
logger.info(logger.ruleset.dict.stacking)  # -> l.__rules["stacking"]
logger.info(logger.ruleset.stacking)  # -> StackingRules object
logger.info(logger.ruleset.stacking.enabled)  # -> l.__rules["stacking"]["enabled"]

# Sample logging tests
logger.info("a\n", 3, 4, 4, "hello world 3")
logger.info("a", 3, 4, 4, "hello world 3", sep="")
logger.info(
    "a\n\n\n\n",
    3,
    4,
    4,
    "hello world 3",
    ["a\n\n\n\n", 3, 4.0, 4.2, "hello world 3"],
    sep="",
)
logger.info("a", 3, 4, 4, "hello world 3", sep=" ")
logger.info("a", 3, 4, 4, "hello world 3", sep="_")
logger.info("a")
logger.info("ajkfhgfhkgdjhd")
logger.info(345)

# Reset the contents of the log.log file
# logger.stream.file.reset("log.log")

logger.debug(3.0)
logger.debug(3.0, {})
logger.debug("Dictionary:", {}, sep=" ")

x = 33
logger.lethal(
    {
        "abcdef": "abcdef",
        "l": ["l", ["l", ["l", ["l", ["l", ["l", []]]]]]],
        "mnopqr": "mnopqr",
        "stuvwx": "stuvwx",
        "hi": (x, logger),
    }
)

logger.error("hi", "bye")
logger.warning("The given tuple is not a valid RGB:", (132, 204, 256))

# Remove the log.log file stream
logger.stream.file.remove("log.log")
