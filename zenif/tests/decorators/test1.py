import unittest
import time
from unittest.mock import patch

from zenif.decorators import (
    retry,
    retry_expo,
    timeout,
    rate_limiter,
    trace,
    suppress_exceptions,
    deprecated,
    type_check,
    log_execution_time,
    cache,
    singleton,
    enforce_types,
    retry_on_exception,
    background_task,
    profile,
    TimeoutError,
    RateLimitError,
)


class TestDecorators(unittest.TestCase):

    def test_retry(self):
        attempts = 0

        @retry(max_retries=3, delay=0.1)
        def flaky_function() -> str:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Not ready yet")
            return "Success"

        result = flaky_function()
        self.assertEqual(result, "Success")
        self.assertEqual(attempts, 3)

        with self.assertRaises(ValueError):

            @retry(max_retries=2, delay=0.1)
            def always_fails() -> None:
                raise ValueError("Always fails")

            always_fails()

    def test_retry_exponential_backoff(self):
        attempts = 0

        @retry_expo(max_retries=4, initial_delay=0.1)
        def flaky_function() -> str:
            nonlocal attempts
            attempts += 1
            if attempts < 4:
                raise ValueError("Not ready yet")
            return "Success"

        start_time = time.time()
        result = flaky_function()
        end_time = time.time()

        self.assertEqual(result, "Success")
        self.assertEqual(attempts, 4)
        self.assertGreater(end_time - start_time, 0.7)  # 0.1 + 0.2 + 0.4 = 0.7

    def test_timeout(self):
        @timeout(1)
        def quick_function() -> str:
            return "Quick"

        @timeout(1)
        def slow_function() -> None:
            time.sleep(2)

        self.assertEqual(quick_function(), "Quick")

        with self.assertRaises(TimeoutError):
            slow_function()

    def test_rate_limiter(self):
        call_count = 0

        @rate_limiter(calls=3, period=1, immediate_fail=True)
        def limited_function() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        for _ in range(3):
            limited_function()

        with self.assertRaises(RateLimitError):
            limited_function()

        time.sleep(1)
        self.assertEqual(limited_function(), 4)

    def test_trace(self):
        @trace
        def sample_function(x: int, y: str) -> str:
            return f"{y} {x}"

        with patch("builtins.print") as mock_print:
            result = sample_function(42, "Answer:")
            self.assertEqual(result, "Answer: 42")
            mock_print.assert_any_call("Calling sample_function(42, 'Answer:')")
            mock_print.assert_any_call("sample_function returned 'Answer: 42'")

    def test_suppress_exceptions(self):
        @suppress_exceptions
        def risky_function() -> None:
            raise ValueError("Oops")

        with patch("builtins.print") as mock_print:
            result = risky_function()
            self.assertIsNone(result)
            mock_print.assert_called_with(
                "Exception suppressed in risky_function: ValueError: Oops"
            )

    def test_deprecated(self):
        # Test basic usage
        @deprecated
        def old_function():
            return "I'm old!"

        result = old_function()
        assert result == "I'm old!"

        # Test with expected_removal argument
        @deprecated(expected_removal="v2.0.0")
        def another_old_function():
            return "I'm also old!"

        result = another_old_function()
        assert result == "I'm also old!"

        # Test with arguments and keyword arguments
        @deprecated
        def old_function_with_args(x, y, z=3):
            return x + y + z

        result = old_function_with_args(1, 2, z=4)
        assert result == 7

    def test_type_check(self):
        @type_check(arg_types=(int, str), return_type=str)
        def typed_function(x: int, y: str) -> str:
            return f"{y} {x}"

        self.assertEqual(typed_function(42, "Answer:"), "Answer: 42")

        with self.assertRaises(TypeError):
            typed_function("42", "Answer:")

        @type_check(arg_types=(int, str), return_type=int)
        def wrong_return_type(x: int, y: str) -> str:
            return f"{y} {x}"

        with self.assertRaises(TypeError):
            wrong_return_type(42, "Answer:")

    def test_log_execution_time(self):
        @log_execution_time
        def slow_function() -> None:
            time.sleep(0.1)

        with patch("builtins.print") as mock_print:
            slow_function()
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            self.assertIn("Execution time for slow_function:", call_args)
            self.assertGreater(float(call_args.split(": ")[1].split()[0]), 0.1)

    def test_cache(self):
        call_count = 0

        @cache
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # First call
        result = expensive_function(2, 3)
        self.assertEqual(result, 5)
        self.assertEqual(call_count, 1)

        # Second call with same arguments (should use cached result)
        result = expensive_function(2, 3)
        self.assertEqual(result, 5)
        self.assertEqual(call_count, 1)  # Call count should not increase

        # Call with different arguments
        result = expensive_function(3, 4)
        self.assertEqual(result, 7)
        self.assertEqual(call_count, 2)

    def test_cache_with_max_size(self):
        call_count = 0

        @cache(max_size=3)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result = expensive_function(1)
        self.assertEqual(result, 2)
        self.assertEqual(call_count, 1)

        # Second call
        result = expensive_function(2)
        self.assertEqual(result, 4)
        self.assertEqual(call_count, 2)

        # Third call (should not evict anything yet)
        result = expensive_function(3)
        self.assertEqual(result, 6)
        self.assertEqual(call_count, 3)

        # Fourth call (should evict the oldest entry)
        result = expensive_function(4)
        self.assertEqual(result, 8)
        self.assertEqual(call_count, 4)

        # Call with evicted argument (should recalculate)
        result = expensive_function(1)
        self.assertEqual(result, 2)
        self.assertEqual(call_count, 5)

        # Call with cached argument
        result = expensive_function(3)
        self.assertEqual(result, 6)
        self.assertEqual(call_count, 5)  # Call count should not increase

    def test_cache_clear(self):
        call_count = 0

        @cache
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result = expensive_function(1)
        self.assertEqual(result, 2)
        self.assertEqual(call_count, 1)

        # Second call (should use cached result)
        result = expensive_function(1)
        self.assertEqual(result, 2)
        self.assertEqual(call_count, 1)

        # Clear the cache
        expensive_function.clear_cache()

        # Call again (should recalculate)
        result = expensive_function(1)
        self.assertEqual(result, 2)
        self.assertEqual(call_count, 2)

    def test_singleton(self):
        @singleton
        class TestClass:
            pass

        instance1 = TestClass()
        instance2 = TestClass()
        self.assertIs(instance1, instance2)

    def test_enforce_types(self):
        @enforce_types
        def test_func(x: int, y: str) -> str:
            return y * x

        self.assertEqual(test_func(3, "a"), "aaa")
        with self.assertRaises(TypeError):
            test_func("3", "a")
        with self.assertRaises(TypeError):
            test_func(3, 2)

    def test_retry_on_exception(self):
        attempts = 0

        @retry_on_exception((ValueError,), max_retries=3, delay=0.1)
        def failing_function():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Not yet!")
            return "Success"

        result = failing_function()
        self.assertEqual(result, "Success")
        self.assertEqual(attempts, 3)

    def test_background_task(self):
        @background_task
        def long_task(duration):
            time.sleep(duration)
            return "Done"

        start = time.time()
        thread = long_task(0.5)
        end = time.time()
        self.assertLess(end - start, 0.5)  # Ensure it returns immediately
        thread.join()
        self.assertGreaterEqual(time.time() - start, 0.5)  # Ensure task completed

    def test_profile(self):
        @profile
        def fibonacci(n):
            if n <= 1:
                return n
            else:
                return fibonacci(n - 1) + fibonacci(n - 2)

        # This test is mainly to ensure the decorator doesn't break the function
        # and that it completes without errors. The actual profiling output
        # is printed to stdout.
        result = fibonacci(10)
        self.assertEqual(result, 55)


if __name__ == "__main__":
    unittest.main()
