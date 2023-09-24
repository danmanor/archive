from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from filepack.compressions.consts import (
    BZ2_SUFFIX,
    GZIP_SUFFIX,
    LZ4_SUFFIX,
    XZ_SUFFIX,
)
from filepack.compressions.types import CompressionObjectTypes


class CompressionType(Enum):
    """Enumeration for different compression types."""

    GZIP = GZIP_SUFFIX
    XZ = XZ_SUFFIX
    LZ4 = LZ4_SUFFIX
    BZ2 = BZ2_SUFFIX


class AbstractCompression(ABC):
    """Abstract base class for different compression types."""

    @abstractmethod
    def open(
        self,
        file_path: str | Path,
        mode: str = "rb",
        compression_level: int = 9,
    ) -> CompressionObjectTypes:
        """Opens the compression file with the given mode and compression level.

        Args:
            file_path: The path to the file.
            mode: The mode in which to open the file.
            compression_level: The level of compression.
        """
        pass
