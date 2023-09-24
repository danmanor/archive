from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, Type

import filetype
import pytz

from filepack.exceptions import OperationNotSupported


def reraise_as(
    exception_class: Type[Exception] = Exception,
) -> Callable[..., Callable[..., Any]]:
    """A decorator that re- raises exceptions as a specified exception class.

    Args:
        exception_class: The class of the exception to raise.

    Returns:
        A decorated function that, when it catches any exception,
        will re-raise it as the given exception_class with the original message and traceback.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise exception_class(f"an error occurred: {str(e)}") from e

        return wrapper

    return decorator


def ensure_instance(
    attribute: str,
) -> Callable[..., Callable[..., Any]]:
    """A decorator that ensures a class instance attribute is not None before calling the method.

    Args:
        attribute: The name of the attribute to check.

    Returns:
        A decorated method that, before proceeding, checks if the specified instance
        attribute is not None. Raises OperationNotSupported if the attribute is None.
    """

    def ensure_instance(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            instance = getattr(self, attribute, None)
            if instance is None:
                raise OperationNotSupported()
            return func(self, *args, **kwargs)

        return wrapper

    return ensure_instance


def format_date_tuple(date_tuple: tuple[int, int, int, int, int, int]) -> str:
    """Formats a date tuple into a string in UTC timezone.

    Args:
        date_tuple: A tuple containing year, month, day, hour, minute, second.

    Returns:
        A string representation of the date and time in UTC timezone.
    """
    israel_tz = pytz.timezone("Asia/Jerusalem")
    localized_dt = israel_tz.localize(datetime(*date_tuple))

    return localized_dt.astimezone(tz=timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S %Z"
    )


def get_file_type_extension(path: Path) -> Optional[str]:
    """Determines the file type of a given file and returns its extension.

    Args:
        path: The filesystem path to the file.

    Returns:
        The file extension if recognized, otherwise raises ValueError.

    Raises:
         ValueError: If the file type is not recognized.
    """
    if (file_type := filetype.guess(path)) is None:
        raise ValueError("given file type is not recognized")
    return file_type.extension
