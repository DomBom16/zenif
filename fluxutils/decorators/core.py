import time
import functools
import signal
from collections import deque
from typing import Callable, TypeVar
from .exceptions import TimeoutError, PermissionError, RateLimitError

T = TypeVar("T")


def retry(
    max_retries: int = 3, delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator_retry(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
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


def retry_exponential_backoff(
    max_retries: int = 3, initial_delay: float = 1.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator_retry_exponential_backoff(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
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


def timeout(seconds: float) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator_timeout(func: Callable[..., T]) -> Callable[..., T]:
        def _handle_timeout(signum: int, frame: any | None) -> None:
            raise TimeoutError(
                f"Function {func.__name__} timed out after {seconds} seconds"
            )

        @functools.wraps(func)
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

        @functools.wraps(func)
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
    @functools.wraps(func)
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
    @functools.wraps(func)
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
    @functools.wraps(func)
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
        @functools.wraps(func)
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
    @functools.wraps(func)
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

    @functools.wraps(func)
    def wrapper_cache(*args: any, **kwargs: any) -> T:
        key = (*args, *sorted(kwargs.items()))
        if key not in cache_dict:
            cache_dict[key] = func(*args, **kwargs)
        return cache_dict[key]

    return wrapper_cache


def requires_permission(
    permission: str,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator_requires_permission(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper_requires_permission(user: any, *args: any, **kwargs: any) -> T:
            if not hasattr(user, "has_permission") or not callable(user.has_permission):
                raise AttributeError("User object must have a 'has_permission' method")
            if not user.has_permission(permission):
                raise PermissionError(
                    f"User does not have the required permission: {permission}"
                )
            return func(user, *args, **kwargs)

        return wrapper_requires_permission

    return decorator_requires_permission
