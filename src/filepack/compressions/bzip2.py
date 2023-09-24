import bz2
from pathlib import Path
from typing import TextIO

from filepack.compressions.models import AbstractCompression, CompressionType


class BzipCompression(AbstractCompression):
    """Represents a compression operation for files using the bzip2 algorithm."""

    def __init__(self, path: Path) -> None:
        """Initializes the BzipCompression with the specified file path.

        Args:
            path: The file system path to the file.
        """
        super().__init__(path=path, extension=CompressionType.BZ2.value)

    def _open(
        self,
        file_path: str | Path,
        mode: str = "r",
        compression_level=9,
    ) -> bz2.BZ2File | TextIO:
        """Opens a file with bzip2 compression.

        Args:
            file_path: The path to the file.
            mode: The mode in which to open the file. Defaults to 'r' for reading.
            compression_level: The compression level, defaults to 9 for maximum compression.

        Returns:
            A BZ2File object that can be used to read or write to the file.
        """
        return bz2.open(
            filename=file_path,
            mode=mode,
            compresslevel=compression_level,
        )
