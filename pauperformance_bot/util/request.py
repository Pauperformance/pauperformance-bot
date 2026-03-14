from functools import wraps
from typing import Any, Callable

from requests import ConnectionError
from requests.models import Response
from retrying import retry


def _retry_on_connection_error(exc: BaseException) -> bool:
    return isinstance(exc, ConnectionError)


def _http_request_retry(
    http_request: Callable[..., Response],
) -> Callable[..., Response]:
    # retries an HTTP request in case of ConnectionError with an exponential
    # backoff policy and additional random waits between 1 and 2 seconds.
    # It gives up after 5 attempts or after 60 seconds have passed.
    @retry(  # type: ignore[untyped-decorator]
        retry_on_exception=_retry_on_connection_error,
        stop_max_attempt_number=5,
        stop_max_delay=60 * 1000,
        wait_random_min=1 * 1000,
        wait_random_max=2 * 1000,
        wait_exponential_multiplier=1000,
    )
    def _execute_with_retry(
        request: Callable[..., Response], *args: Any, **kwargs: Any
    ) -> Response:
        return http_request(request, *args, **kwargs)

    return wraps(http_request)(_execute_with_retry)


@_http_request_retry
def execute_http_request(
    request_fn: Callable[..., Response],
    url: str,
    timeout: tuple[int, int] = (3 * 20, 120),
    headers: dict[str, str] = {},
) -> Response:
    # Assumes the request_fn is from requests module.
    # Timeout is a tuple (connection_timeout, read_timeout).
    # Further details here:
    # https://3.python-requests.org/user/quickstart/#timeouts
    # Caller should catch ConnectionError and HTTPError, or more broadly
    # requests.exceptions.RequestException
    response = request_fn(url, timeout=timeout, headers=headers)
    response.raise_for_status()
    return response
