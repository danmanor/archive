from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, Type

import filetype


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
