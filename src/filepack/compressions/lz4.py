from pathlib import Path
from typing import TextIO

import lz4.frame

from filepack.compressions.models import AbstractCompression


class LZ4Compression(AbstractCompression):
    """Represents a compression operation for files using the LZ4 algorithm."""

    def open(
        self,
        file_path: str | Path,
        mode: str = "r",
        compression_level=9,
    ) -> lz4.frame.LZ4FrameFile | TextIO:
        """Opens a file with LZ4 compression.

        Args:
            file_path: The path to the file.
            mode: The mode in which to open the file. Defaults to 'r'.
            compression_level: The compression level, with 9 being the default high compression preset.

        Returns:
            An LZ4FrameFile object that can be used to read or write to the file.
        """
        return lz4.frame.open(
            filename=file_path,
            mode=mode,
            compression_level=compression_level,
        )
