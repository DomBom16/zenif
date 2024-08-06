import asyncio
import os
from io import StringIO
from src.log import Logger, LogLevel, StreamHandler, FileHandler, Formatter


class TestLogger:
    def __init__(self):
        self.test_log_file = "test_log.txt"
        self.custom_stream = StringIO()

    async def run_tests(self):
        print("Starting Logger tests...")

        await self.test_basic_logging()
        await self.test_log_levels()
        await self.test_custom_handlers()
        await self.test_custom_formatters()
        await self.test_async_logging()
        await self.test_context_manager()
        await self.test_file_logging()
        await self.test_filtering()

        print("All tests completed successfully!")

    async def test_basic_logging(self):
        print("\nTesting basic logging...")
        rules = {"log_line": {"format": "{timestamp} [{level}] {message}"}}
        logger = Logger(rules)
        logger.info("This is a test info message")
        logger.error("This is a test error message")
        print("Basic logging test completed.")

    async def test_log_levels(self):
        print("\nTesting all log levels...")
        logger = Logger()
        log_levels = [
            "trace",
            "debug",
            "info",
            "success",
            "warning",
            "error",
            "critical",
        ]
        for level in log_levels:
            getattr(logger, level)(f"This is a {level} message")
        print("Log levels test completed.")

    async def test_custom_handlers(self):
        print("\nTesting custom handlers...")
        logger = Logger()
        custom_formatter = Formatter("CUSTOM: {level} - {message}")
        custom_handler = StreamHandler(self.custom_stream, custom_formatter)
        logger.add_handler(custom_handler)
        logger.info("This message should go to the custom stream")
        assert (
            "CUSTOM: INFO - This message should go to the custom stream"
            in self.custom_stream.getvalue()
        )
        logger.remove_handler(custom_handler)
        print("Custom handlers test completed.")

    async def test_custom_formatters(self):
        print("\nTesting custom formatters...")
        rules = {
            "log_line": {
                "format": "CUSTOM FORMAT: {timestamp:%Y-%m-%d} {level} {message}"
            }
        }
        logger = Logger(rules)
        logger.info("This message should use the custom format")
        # You'd need to capture the output to verify the format
        print("Custom formatters test completed.")

    async def test_async_logging(self):
        print("\nTesting async logging...")
        rules = {"async_logging": {"enabled": True}}
        logger = Logger(rules)
        logger.start_async_logging()
        for i in range(5):
            logger.info(f"Async log message {i}")
        await asyncio.sleep(0.1)  # Give some time for async logging to process
        logger.stop_async_logging()
        print("Async logging test completed.")

    async def test_context_manager(self):
        print("\nTesting context manager...")
        logger = Logger()
        logger.info("This should be logged")
        with logger.context(filtering={"min_level": LogLevel.ERROR}):
            logger.info("This should not be logged")
            logger.error("This should be logged")
        logger.info("This should be logged again")
        print("Context manager test completed.")

    async def test_file_logging(self):
        print("\nTesting file logging...")
        rules = {"output": {"output_to_file": True, "file_path": self.test_log_file}}
        logger = Logger(rules)
        logger.info("This should be written to the file")
        logger.error("This error should also be in the file")

        with open(self.test_log_file, "r") as f:
            content = f.read()
            assert "This should be written to the file" in content
            assert "This error should also be in the file" in content

        os.remove(self.test_log_file)
        print("File logging test completed.")

    async def test_filtering(self):
        print("\nTesting log filtering...")
        rules = {
            "filtering": {
                "min_level": LogLevel.WARNING,
                "exclude_messages": ["excluded"],
                "include_only_messages": ["important"],
            }
        }
        logger = Logger(rules)
        logger.info("This should not be logged due to level")
        logger.warning("This warning should be logged")
        logger.error("This error with excluded should not be logged", "excluded")
        logger.critical("This critical important message should be logged", "important")
        print("Filtering test completed.")


async def main():
    test_logger = TestLogger()
    await test_logger.run_tests()


if __name__ == "__main__":
    asyncio.run(main())
