import lzma
from pathlib import Path
from typing import TextIO

from filepack.compressions.models import AbstractCompression


class XZCompression(AbstractCompression):
    """Represents a compression operation for files using the XZ algorithm."""

    def open(
        self,
        file_path: str | Path,
        mode: str = "r",
        compression_level=None,
    ) -> lzma.LZMAFile | TextIO:
        """Opens a file with XZ compression.

        Args:
            file_path: The path to the file.
            mode: The mode in which to open the file. Defaults to 'r'.
            compression_level: The compression level. If None, the default is used.

        Returns:
            An LZMAFile object that can be used to read or write to the file.
        """
        return lzma.open(
            filename=file_path, mode=mode, preset=compression_level
        )
