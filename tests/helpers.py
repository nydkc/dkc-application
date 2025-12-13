"""Common test helper functions."""
import time


def wait_for_datastore_consistency(check_func, timeout=10, interval=0.5):
    """
    Wait for datastore to become eventually consistent.

    Args:
        check_func: Callable that returns True when consistency is achieved
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds

    Returns:
        bool: True if consistency achieved, False if timeout

    Raises:
        AssertionError: If timeout is reached
    """
    iterations = int(timeout / interval)
    for _ in range(iterations):
        if check_func():
            return True
        time.sleep(interval)

    raise AssertionError(f"Datastore consistency wait timed out after {timeout}s")
