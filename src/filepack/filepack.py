from pathlib import Path

from filepack.archive import Archive
from filepack.compression import Compression


class FilePack(Archive, Compression):
    """Provides a unified interface for interacting with archive and compression operations."""

    def __init__(self, path: str | Path) -> None:
        errors: list[Exception] = []

        try:
            Archive.__init__(self, path)
        except ValueError as e:
            errors.append(e)

        try:
            Compression.__init__(self, path)
        except FileNotFoundError as e:
            errors.append(e)

        if len(errors) == 2:
            raise ExceptionGroup(
                "the given path can't be used for archiving or compression",
                errors,
            )
