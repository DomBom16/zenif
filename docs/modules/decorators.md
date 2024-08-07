# Decorators Module

FluxUtils provides a set of powerful decorators to enhance your Python functions. These decorators offer various functionalities such as retry mechanisms, timeout handling, rate limiting, and more.

## Available Decorators

Below are the available decorators.

### retry

Retries the decorated function a specified number of times with a delay between attempts.

```python
from fluxutils.decorators import retry

@retry(max_retries=3, delay=1.0)
def flaky_function():
    # Your code here
    # If an exception is raised, the function will be retried up to 3 times
    # with a 1-second delay between attempts
```

### retry_exponential_backoff

Similar to `retry`, but with an exponential backoff delay between attempts.

```python
from fluxutils.decorators import retry_exponential_backoff

@retry_exponential_backoff(max_retries=3, initial_delay=1.0)
def flaky_function():
    # Your code here
    # If an exception is raised, the function will be retried up to 3 times
    # with delays of 1, 2, and 4 seconds between attempts
```

### retry_on_exception

Retries the function only when specific exceptions are raised.

```python
from fluxutils.decorators import retry_on_exception

@retry_on_exception((ValueError, TypeError), max_retries=3, delay=0.5)
def potentially_failing_function(x):
    if x < 0:
        raise ValueError("x must be non-negative")
    return x ** 0.5

print(potentially_failing_function(4))  # Works fine
print(potentially_failing_function(-1))  # Retries three times, then raises ValueError
```

### timeout

Sets a maximum execution time for the decorated function.

```python
from fluxutils.decorators import timeout

@timeout(seconds=5)
def long_running_function():
    import time
    time.sleep(10)
    return "This will never be reached"

try:
    result = long_running_function()
except TimeoutError:
    print("Function timed out")
```

### rate_limiter

Limits the rate at which the decorated function can be called, which is useful for controlling access to rate-limited APIs or resources.

```python
import time
from fluxutils.decorators import rate_limiter

@rate_limiter(calls=3, period=10, immediate_fail=True)
def limited_api_call(call_id):
    print(f"API call {call_id} executed")
    return f"Result of call {call_id}"

# Usage
start_time = time.time()

for i in range(5):
    try:
        result = limited_api_call(i)
        print(f"Call {i} succeeded: {result}")
    except RateLimitError as e:
        print(f"Call {i} failed: {e}")
    
    if i < 4:  # Don't sleep after the last call
        time.sleep(2)  # Wait 2 seconds between calls

end_time = time.time()
print(f"Total time: {end_time - start_time:.2f} seconds")
```

### trace

Logs the function call, its arguments, and the return value.

```python
from fluxutils.decorators import trace

@trace
def function_to_trace(arg1, arg2):
    # Your code here
    # The function call, arguments, and return value will be printed
```

### suppress_exceptions

Catches and suppresses any exceptions raised by the decorated function.

```python
from fluxutils.decorators import suppress_exceptions

@suppress_exceptions
def risky_function():
    # Your code here
    # Any exceptions raised will be caught and suppressed
```

### deprecated

Marks a function as deprecated and issues a warning when it's used.

```python
from fluxutils.decorators import deprecated

@deprecated
def old_function():
    # Your code here
    # A deprecation warning will be issued when this function is called
```

### type_check

Checks the types of arguments and return value against specified types.

```python
from fluxutils.decorators import type_check

@type_check(arg_types=(int, str), return_type=str)
def typed_function(num: int, text: str) -> str:
    # Your code here
    # The decorator will check if num is an int, text is a str,
    # and the return value is a str
```

### log_execution_time

Logs the execution time of the decorated function.

```python
from fluxutils.decorators import log_execution_time

@log_execution_time
def timed_function():
    # Your code here
    # The execution time of this function will be logged
```

### cache

Caches the return value of the function based on its arguments. The cache can be extremely useful for functions with a recursive nature, and in some cases running boatloads faster.

```python
from fluxutils.decorators import cache

@cache
def expensive_function(arg):
    # Your code here
    # The return value will be cached based on the 'arg' value
```

### singleton

Ensures only one instance of a class is created.

```python
from fluxutils.decorators import singleton

@singleton
class DatabaseConnection:
    def __init__(self):
        self.connection = "Connected"

    def query(self):
        return f"Querying {self.connection}"

# This will create only one instance
db1 = DatabaseConnection()
db2 = DatabaseConnection()
print(db1 is db2)  # Output: True
```

### enforce_types

Strictly enforces type hints on function arguments and return values.

```python
from fluxutils.decorators import enforce_types

@enforce_types
def greet(name: str, times: int) -> str:
    return f"Hello {name}! " * times

print(greet("Alice", 3))  # Works fine
print(greet("Bob", "2"))  # Raises TypeError: Argument times must be <class 'int'>
```

### background_task

Runs the decorated function in a separate thread.

```python
from fluxutils.decorators import background_task

@background_task
def long_running_task(duration):
    import time
    time.sleep(duration)
    print(f"Task completed after {duration} seconds")

# This will start the task in the background and immediately return
thread = long_running_task(5)
print("Main thread continues immediately")
thread.join()  # Wait for the background task to complete
```

### profile

Profiles the function's execution and logs performance metrics, including memory usage. This decorator handles recursive calls correctly, only profiling the outermost call.

```python
from fluxutils.decorators import profile

@profile
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Result: {result}")
```

This decorator will print out execution time, memory usage, and a summary of the profiling results for the entire function execution, including any recursive calls.

## Mixing Decorators

In addition to a wide range of decorators, these decorators can be used in a combined manner to add powerful functionality to your Python functions. For example, the following combines the use of the `cache` and `profile` decorators to compare the difference between using a cache and without:

```python
from fluxutils.decorators import profile, cache

@profile
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

@profile
@cache
def cached_fibonacci(n):
    if n <= 1:
        return n
    else:
        return cached_fibonacci(n-1) + cached_fibonacci(n-2)

# Output:
# Function: fibonacci
# Time taken:           26.1033 seconds
# Current memory usage: 0.009442 MB
# Peak memory usage:    0.010219 MB
# Profile:
#          22811546 function calls (4 primitive calls) in 26.103 seconds

# Function: cached_fibonacci
# Time taken:           0.0005 seconds
# Current memory usage: 0.015030 MB
# Peak memory usage:    0.015749 MB
# Profile:
#          294 function calls (135 primitive calls) in 0.000 seconds
```

For more detailed information on each decorator and advanced usage examples, please refer to the full documentation.
