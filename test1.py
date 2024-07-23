from fluxlog import FluxLogger

l = FluxLogger(rules={"stacking": {"enable_stacking": False}})

l.info("a\n", 3, 4, 4, "hello world 3")
l.info("a\n\n", 3, 4, 4, "hello world 3", sep="")
l.info("a", 3, 4, 4, "hello world 3", sep=" ")
l.info("a", 3, 4, 4, "hello world 3", sep="_")
l.info("a")
l.info("ajkfhgfhkgdjhd")
l.info(345)
l.debug(3.0)
l.debug(3.0, {})
l.critical(
    {
        "abcdef": "abcdef",
        "l": ["l", ["l", ["l", ["l", ["l", ["l", []]]]]]],
        "mnopqr": "mnopqr",
        "stuvwx": "stuvwx",
        "hi": l,
    }
)
