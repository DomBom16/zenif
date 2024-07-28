from fluxlog import FluxLogger

# l = FluxLogger(rules={"stacking": {"stacking_enabled": False}})
l = FluxLogger()


def superlongfunctionname():
    l.error("Could", "not", "run function")


superlongfunctionname()

l.info("a\n", 3, 4, 4, "hello world 3")
l.info("a\n\n\n\n", 3, 4, 4, "hello world 3", sep="")
l.info(
    "a\n\n\n\n",
    3,
    4,
    4,
    "hello world 3",
    ["a\n\n\n\n", 3, 4.0, 4.2, "hello world 3"],
    sep="",
)
l.info("a", 3, 4, 4, "hello world 3", sep=" ")
l.info("a", 3, 4, 4, "hello world 3", sep="_")
l.info("a")
l.info("ajkfhgfhkgdjhd")
l.info(345)
l.debug(3.0)
l.debug(3.0, {})
l.debug("Dictionary:", {}, sep=" ")
x = 33
l.critical(
    {
        "abcdef": "abcdef",
        "l": ["l", ["l", ["l", ["l", ["l", ["l", []]]]]]],
        "mnopqr": "mnopqr",
        "stuvwx": "stuvwx",
        "hi": (x, l),
    }
)

l.error("hi", "bye")

superlongfunctionname()
