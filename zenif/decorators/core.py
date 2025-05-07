import cProfile
import functools
import io
import pstats
import signal
import time
import tracemalloc
from collections import OrderedDict, deque
from functools import wraps
from inspect import signature
from threading import Thread
from typing import Callable, TypeVar

from ..log import Logger
from .exceptions import RateLimitError, TimeoutError

logger = Logger(
    ruleset={"timestamps": {"always_show": True}, "log_line": {"format": "simple"}}
)

T = TypeVar("T")


def retry(
    max_retries: int = 3, delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry a function a specified number of times with a delay between attempts.

    This decorator takes a function and retries it a specified number of times
    with a delay between attempts. The delay is specified in seconds and must be
    a non-negative number.

    The function will be retried up to `max_retries` times. If the function still
    raises an exception after `max_retries` attempts, the exception will be
    re-raised.

    :param max_retries: The maximum number of times to retry the function.
        Defaults to 3.
    :param delay: The time in seconds to wait between attempts. Defaults to 1.0.
    """

    def decorator_retry(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper_retry(*args: any, **kwargs: any) -> T:
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
                    if attempts >= max_retries:
                        raise
                    time.sleep(max(0, delay))  # Ensure non-negative delay
            raise RuntimeError("Exceeded maximum retries")

        return wrapper_retry

    return decorator_retry


def retry_expo(
    max_retries: int = 3, initial_delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry a function a specified number of times with an exponential backoff
    delay between attempts.

    This decorator takes a function and retries it a specified number of times
    with an exponential backoff delay between attempts. The delay will increase
    by a factor of two for each attempt, starting from `initial_delay`.

    The function will be retried up to `max_retries` times. If the function still
    raises an exception after `max_retries` attempts, the exception will be
    re-raised.

    :param max_retries: The maximum number of times to retry the function.
        Defaults to 3.
    :param initial_delay: The time in seconds to wait between the first and
        second attempts. Defaults to 1.0.
    """

    def decorator_retry_expo_backoff(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper_retry_expo_backoff(*args: any, **kwargs: any) -> T:
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
                    if attempts >= max_retries:
                        raise
                    delay = initial_delay * (2 ** (attempts - 1))
                    time.sleep(max(0, delay))  # Ensure non-negative delay
            raise RuntimeError("Exceeded maximum retries")

        return wrapper_retry_expo_backoff

    return decorator_retry_expo_backoff


def timeout(seconds: float) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Set a maximum execution time for a function.

    This decorator takes a function and sets a maximum execution time. If the
    function takes longer than the specified time to execute, a TimeoutError
    will be raised.

    The timeout is specified in seconds and must be a non-negative number.

    On Unix-like systems, the SIGALRM signal is used to enforce the timeout. On
    other systems (e.g., Windows), the function will be executed without any
    timeout.

    :param seconds: The maximum time in seconds to allow the function to execute.
    """

    def decorator_timeout(func: Callable[..., T]) -> Callable[..., T]:
        def _handle_timeout(signum: int, frame: any | None) -> None:
            raise TimeoutError(
                f"Function {func.__name__} timed out after {seconds} seconds"
            )

        wraps(func)

        def wrapper_timeout(*args: any, **kwargs: any) -> T:
            # Use SIGALRM only on Unix-like systems
            if hasattr(signal, "SIGALRM"):
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(int(seconds))
                try:
                    return func(*args, **kwargs)
                finally:
                    signal.alarm(0)  # Disable the alarm
            else:
                # Fallback for systems without SIGALRM (e.g., Windows)
                return func(*args, **kwargs)

        return wrapper_timeout

    return decorator_timeout


def rate_limiter(
    calls: int, period: float, immediate_fail: bool = True
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Limits the rate at which the decorated function can be called.

    This decorator takes a function and limits the rate at which it can be
    called. The rate is specified in terms of the maximum number of calls
    allowed within a given time period.

    The function will be called immediately if the rate limit is not exceeded.
    If the rate limit is exceeded and `immediate_fail` is `True`, a
    `RateLimitError` will be raised. If `immediate_fail` is `False`, the
    function will block until the rate limit is no longer exceeded.

    :param calls: The maximum number of calls allowed within the given time period.
    :param period: The time period in which the maximum number of calls is allowed.
    :param immediate_fail: If `True`, raise a `RateLimitError` if the rate limit is
        exceeded. If `False`, block until the rate limit is no longer exceeded.
    """

    def decorator_rate_limiter(func: Callable[..., T]) -> Callable[..., T]:
        call_times: deque = deque(maxlen=calls)

        @wraps(func)
        def wrapper_rate_limiter(*args: any, **kwargs: any) -> T:
            current_time = time.monotonic()  # Use monotonic time for better precision
            while call_times and current_time - call_times[0] > period:
                call_times.popleft()

            if len(call_times) < calls:
                call_times.append(current_time)
                return func(*args, **kwargs)
            else:
                if immediate_fail:
                    raise RateLimitError(
                        f"Function {func.__name__} rate-limited. Try again later."
                    )
                else:
                    wait_time = max(0, period - (current_time - call_times[0]))
                    time.sleep(wait_time)
                    return wrapper_rate_limiter(*args, **kwargs)

        return wrapper_rate_limiter

    return decorator_rate_limiter


def trace(func: Callable[..., T]) -> Callable[..., T]:
    """
    A decorator that prints the arguments and return value of the decorated function.

    When the decorated function is called, this decorator will print the name of the
    function, the arguments passed to it, and the return value. If the function raises
    an exception, the decorator will print the exception type and message.

    :param func: The function to be decorated.
    :return: A decorated version of the function that prints the arguments and return
        value.
    """

    @wraps(func)
    def wrapper_trace(*args: any, **kwargs: any) -> T:
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        try:
            result = func(*args, **kwargs)
            print(f"{func.__name__} returned {result!r}")
            return result
        except Exception as e:
            print(f"{func.__name__} raised {type(e).__name__}: {str(e)}")
            raise

    return wrapper_trace


def suppress_exceptions(func: Callable[..., T | None]) -> Callable[..., T | None]:
    """
    Suppresses any exceptions raised by the decorated function.

    When the decorated function raises an exception, this decorator will print the
    exception type and message, and return None instead of propagating the exception.

    :param func: The function to be decorated.
    :return: A decorated version of the function that suppresses any exceptions.
    """

    @wraps(func)
    def wrapper_suppress_exceptions(*args: any, **kwargs: any) -> T | None:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(
                f"Exception suppressed in {func.__name__}: {type(e).__name__}: {str(e)}"
            )
            return None

    return wrapper_suppress_exceptions


def deprecated(
    func: Callable[..., T] | None = None, *, expected_removal: str | None = None
) -> Callable[..., T]:
    """
    Marks a function as deprecated and issues a warning when it's used.

    This decorator can be used to mark a function as deprecated. When the
    decorated function is called, a warning message will be logged indicating
    that the function is deprecated and may be removed in a future version.
    An optional `expected_removal` parameter can be provided to specify the
    version in which the function is expected to be removed.

    :param func: The function to be decorated. If None, the decorator is
        returned for use with a function.
    :param expected_removal: An optional string specifying the version in
        which the function is expected to be removed.
    :return: A decorated version of the function that logs a deprecation
        warning when called.
    """

    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        @wraps(f)
        def wrapper_deprecated(*args: any, **kwargs: any) -> T:
            warning_message = (
                f"{f.__name__} is deprecated and will be removed in a future version"
            )
            if expected_removal:
                warning_message += f"\n> Expected to be removed by {expected_removal}"
            logger.warning(warning_message)
            return f(*args, **kwargs)

        return wrapper_deprecated

    if func is None:
        return decorator
    else:
        return decorator(func)


def type_check(
    arg_types: tuple[type, ...] | None = None, return_type: type | None = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Checks the types of arguments and return value against specified types.

    This decorator can be used to ensure that the arguments passed to a function
    are of the correct type, and that the return value is of the correct type.

    :param arg_types: A tuple of types to check the arguments against. If None,
        no argument type checking is performed.
    :param return_type: The type to check the return value against. If None, no
        return type checking is performed.
    :return: A decorated version of the function that performs type checking on
        arguments and return value.
    """

    def decorator_type_check(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper_type_check(*args: any, **kwargs: any) -> T:
            if arg_types:
                for arg, expected_type in zip(args, arg_types):
                    if not isinstance(arg, expected_type):
                        raise TypeError(
                            f"Argument {arg!r} does not match type {expected_type}"
                        )
            result = func(*args, **kwargs)
            if return_type and not isinstance(result, return_type):
                raise TypeError(
                    f"Return value {result!r} does not match type {return_type}"
                )
            return result

        return wrapper_type_check

    return decorator_type_check


def log_execution_time(func: Callable[..., T]) -> Callable[..., T]:
    """
    Logs the execution time of the decorated function.

    This decorator can be used to profile functions and methods. The execution time
    is printed to the console after the function is called.

    :param func: The function to be decorated.
    :return: A decorated version of the function that logs the execution time.
    """

    @wraps(func)
    def wrapper_log_execution_time(*args: any, **kwargs: any) -> T:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(
            f"Execution time for {func.__name__}: {end_time - start_time:.6f} seconds"
        )
        return result

    return wrapper_log_execution_time


def cache(
    func: Callable[..., T] | None = None, *, max_size: int | None = None
) -> Callable[..., T]:
    """
    Caches the result of a function so that it is only computed once.

    The cache is implemented as a least-recently-used (LRU) cache. The cache
    size can be limited by providing the `max_size` parameter. If the cache
    size is exceeded, the oldest item will be discarded.

    The cache is stored as an instance variable of the decorated function. The
    cache can be cleared by calling the `clear_cache` method of the decorated
    function.

    :param func: The function to be decorated. If None, the decorator is
        returned for use with a function.
    :param max_size: The maximum size of the cache. If None, there is no limit.
    :return: A decorated version of the function that caches its result.
    """

    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        cache_dict: OrderedDict = OrderedDict()

        @wraps(f)
        def wrapper_cache(*args: any, **kwargs: any) -> T:
            key = (*args, *sorted(kwargs.items()))
            if key not in cache_dict:
                result = f(*args, **kwargs)
                cache_dict[key] = result
                if max_size is not None and len(cache_dict) > max_size:
                    cache_dict.popitem(last=False)  # Remove the oldest item
            return cache_dict[key]

        # Add a method to clear the cache
        wrapper_cache.clear_cache = cache_dict.clear

        return wrapper_cache

    if func is None:
        return decorator
    else:
        return decorator(func)


def singleton(cls):
    """
    Ensures only one instance of a class is created.

    This decorator can be used to turn a class into a singleton. The decorator
    caches the instance of the class and returns the same instance every time
    the class is instantiated. The instance is stored in a dictionary with the
    class as the key.

    :param cls: The class to be decorated.
    :return: A decorated version of the class that caches its instance.
    """
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def enforce_types(func):
    """
    Enforces type annotations on function arguments and return value.

    This decorator validates the types of arguments passed to a function
    against its type annotations. If any argument does not match the
    specified type, a TypeError is raised. It also checks the return
    value against the function's return type annotation.

    :param func: The function to be decorated.
    :return: A decorated version of the function that enforces type
             annotations on its arguments and return value.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = signature(func)
        bound_args = sig.bind(*args, **kwargs)
        for name, value in bound_args.arguments.items():
            if name in sig.parameters:
                param = sig.parameters[name]
                if param.annotation != param.empty:
                    if not isinstance(value, param.annotation):
                        raise TypeError(f"Argument {name} must be {param.annotation}")

        result = func(*args, **kwargs)
        if sig.return_annotation != sig.empty:
            if not isinstance(result, sig.return_annotation):
                raise TypeError(f"Return value must be {sig.return_annotation}")
        return result

    return wrapper


def retry_on_exception(exceptions, max_retries=3, delay=1):
    """
    Retry a function a specified number of times with a delay between attempts.

    This decorator takes a function and retries it a specified number of times
    with a delay between attempts. The delay is specified in seconds and must be
    a non-negative number.

    The function will be retried up to `max_retries` times. If the function still
    raises an exception after `max_retries` attempts, the exception will be
    re-raised.

    :param exceptions: A tuple of exceptions to catch and retry on.
    :param max_retries: The maximum number of times to retry the function.
        Defaults to 3.
    :param delay: The time in seconds to wait between attempts. Defaults to 1.0.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
            return func(*args, **kwargs)  # This line should never be reached

        return wrapper

    return decorator


def background_task(func):
    """
    Runs the decorated function in a separate thread.

    This decorator takes a function and runs it in a separate thread when called.
    The return value of the decorated function is a Thread object that can be
    used to wait for the thread to complete (e.g., by calling join()).
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


_profiler_active = False


def profile(func):
    """
    Profiles the execution of the decorated function, capturing performance metrics.

    This decorator measures the execution time, memory usage, and function call statistics
    of the decorated function. It handles recursive calls correctly, profiling only the
    outermost call to avoid duplicating metrics. The profiling results, including a summary
    of the function calls, are printed to the console.

    :param func: The function to be profiled.
    :return: A decorated version of the function that logs execution time,
            memory usage, and profiling statistics.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _profiler_active

        if not _profiler_active:
            _profiler_active = True
            profiler = cProfile.Profile()
            try:
                tracemalloc.start()
                start_time = time.time()
                profiler.enable()
                result = func(*args, **kwargs)
                profiler.disable()
                end_time = time.time()
            finally:
                try:
                    current, peak = tracemalloc.get_traced_memory()
                except RuntimeError:
                    current, peak = 0, 0
                tracemalloc.stop()
                _profiler_active = False

            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
            ps.print_stats(10)  # Print top 10 lines

            print(f"{'Function:'.ljust(25)} {func.__name__}")
            print(f"{'Time taken:'.ljust(25)} {end_time - start_time:.4f} seconds")
            print(f"{'Current memory usage:'.ljust(25)} {current / 10**6:.6f} MB")
            print(f"{'Peak memory usage:'.ljust(25)} {peak / 10**6:.6f} MB")
            print("Profile:")
            print(s.getvalue())
        else:
            result = func(*args, **kwargs)

        return result

    return wrapper
