from zenif.log import Logger
import sys

# Initialize a Logger instance
l = Logger()

fstream = l.stream.file
nstream = l.stream.normal

group = l.fhgroup(
    fstream.add("log1.log"),
    l.fhgroup(fstream.add("log2.log"), fstream.add("log3.log")),
    l.fhgroup(fstream.add("log4.log")),
)

group.reset()
group.modify(
    ruleset={
        "timestamps": {
            "always_show": True,
            "use_utc": True,
        },
        "log_line": {"format": "noalign"},
    }
)


def superlongfunctionname():
    l.error("Could", "not", "run function")


# Tests truncation of long function names
superlongfunctionname()

l.info(l.ruleset.dict.all)  # -> l.__rules
l.info(l.ruleset.dict.stacking)  # -> l.__rules["stacking"]
l.info(l.ruleset.stacking)  # -> StackingRules object
l.info(l.ruleset.stacking.enabled)  # -> l.__rules["stacking"]["enabled"]

# Sample logging tests
l.info("a\n", 3, 4, 4, "hello world 3")
l.info("a", 3, 4, 4, "hello world 3", sep="")
l.info(
    "a\n\n\n\n", 3, 4, 4, "hello world 3", ["a\n\n\n\n", 3, 4.0, 4.2, "hello world 3"]
)
l.info("a", 3, 4, 4, "hello world 3", sep=" ")
l.info("a", 3, 4, 4, "hello world 3", sep="_")
l.info("a")
l.info("ajkfhgfhkgdjhd")
l.info(345)

l.debug(3.0)
l.debug(3.0, {})
l.debug("Dictionary:", {}, sep=" ")

nstream.modify(sys.stdout, ruleset={"timestamps": {"always_show": True}})


x = 33
l.lethal(
    {
        "abcdef": "abcdef",
        "l": ["l", ["l", ["l", ["l", ["l", ["l", []]]]]]],
        "mnopqr": "mnopqr",
        "stuvwx": "stuvwx",
        "hi": (x, l),
    }
)

l.error("hi", "bye")
l.warning("The given tuple is not a valid RGB:", (132, 204, 256))

# Remove the log.log file stream
fstream.remove("log1.log")

l.warning("The given tuple is not a valid RGB:", (132, 204, 256))
l.warning("The given tuple is not a valid RGB:", (132, 204, 256))
l.warning("The given tuple is not a valid RGB:", (132, 204, 256))


# Create a file handler group
fh_group = l.fhgroup(
    fstream.add("log1.log"), fstream.add("log2.log"), fstream.add("log3.log")
)

l.debug("Added groups:", fh_group.file_paths)


# Modify all files in the group


fh_group.modify({"timestamps": {"use_utc": False}})

# Add another file to the group

l.debug("Added groups:", fh_group.add("log4.log"))


# # Reset all files in the group
# fh_group.reset()

# Remove a specific file from the group
fh_group.remove("log2.log", l.fhgroup("log3.log", l.fhgroup("log1.log")))

l.debug("Logs 1-3 won't get this message!")

# # Remove all files in the group
# fh_group.remove_all()

import sys
from io import StringIO

sh_group1 = l.shgroup(sys.stdout)
sh_group2 = l.shgroup(sys.stderr)
custom_stream = StringIO()
combined_sh_group = l.shgroup(sh_group1, sh_group2, custom_stream)

l.error("hello")
l.error("hello")
l.error("hello")
