import gzip
from pathlib import Path
from typing import TextIO

from filepack.compressions.models import AbstractCompression, CompressionType


class GzipCompression(AbstractCompression):
    """Represents a compression operation for files using the gzip algorithm."""

    def __init__(self, path: Path) -> None:
        """Initializes the GzipCompression with the specified file path.

        Args:
            path: The file system path to the file.
        """
        super().__init__(path=path, extension=CompressionType.GZIP.value)

    def _open(
        self,
        file_path: str | Path,
        mode: str = "r",
        compression_level=9,
    ) -> gzip.GzipFile | TextIO:
        """Opens a file with gzip compression.

        Args:
            file_path: The path to the file.
            mode: The mode in which to open the file. Defaults to 'r' for reading.
            compression_level: The compression level, defaults to 9 for maximum compression.

        Returns:
            A GzipFile object that can be used to read or write to the file.
        """
        return gzip.open(
            filename=file_path,
            mode=mode,
            compresslevel=compression_level,
        )
