import time
from functools import wraps
import signal
from collections import deque
from typing import Callable, TypeVar, Union
from inspect import signature
from threading import Thread
import time
import functools
import cProfile
import pstats
import io
import tracemalloc
from .exceptions import TimeoutError, RateLimitError
from .core import deprecated

T = TypeVar("T")


def retry(
    max_retries: int = 3, delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator_retry(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper_retry(*args: any, **kwargs: any) -> T:
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_retries:
                        raise
                    time.sleep(max(0, delay))  # Ensure non-negative delay
            raise RuntimeError("Exceeded maximum retries")

        return wrapper_retry

    return decorator_retry

@deprecated
def retry_exponential_backoff(
    max_retries: int = 3, initial_delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator_retry_exponential_backoff(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper_retry_exponential_backoff(*args: any, **kwargs: any) -> T:
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_retries:
                        raise
                    delay = initial_delay * (2 ** (attempts - 1))
                    time.sleep(max(0, delay))  # Ensure non-negative delay
            raise RuntimeError("Exceeded maximum retries")

        return wrapper_retry_exponential_backoff

    return decorator_retry_exponential_backoff

def retry_expo(
    max_retries: int = 3, initial_delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator_retry_expo_backoff(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper_retry_expo_backoff(*args: any, **kwargs: any) -> T:
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_retries:
                        raise
                    delay = initial_delay * (2 ** (attempts - 1))
                    time.sleep(max(0, delay))  # Ensure non-negative delay
            raise RuntimeError("Exceeded maximum retries")

        return wrapper_retry_expo_backoff

    return decorator_retry_expo_backoff


def timeout(seconds: float) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator_timeout(func: Callable[..., T]) -> Callable[..., T]:
        def _handle_timeout(signum: int, frame: Union[any, None]) -> None:
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


import warnings


def deprecated(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper_deprecated(*args: any, **kwargs: any) -> T:
        warnings.warn(
            f"{func.__name__} is deprecated and will be removed in a future version",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper_deprecated


def type_check(
    arg_types: tuple[type, ...] | None = None, return_type: type | None = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
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


def cache(func: Callable[..., T]) -> Callable[..., T]:
    cache_dict: dict[tuple[any, ...], any] = {}

    @wraps(func)
    def wrapper_cache(*args: any, **kwargs: any) -> T:
        key = (*args, *sorted(kwargs.items()))
        if key not in cache_dict:
            cache_dict[key] = func(*args, **kwargs)
        return cache_dict[key]

    return wrapper_cache


def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def enforce_types(func):
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
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
            return func(*args, **kwargs)  # This line should never be reached

        return wrapper

    return decorator


def background_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


_profiler_active = False


def profile(func):
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

            print(f"Function: {func.__name__}")
            print(f"{"Time taken:".ljust(21)} {end_time - start_time:.4f} seconds")
            print(f"Current memory usage: {current / 10**6:.6f} MB")
            print(f"{"Peak memory usage:".ljust(21)} {peak / 10**6:.6f} MB")
            print("Profile:")
            print(s.getvalue())
        else:
            result = func(*args, **kwargs)

        return result

    return wrapper
