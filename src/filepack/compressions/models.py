import os
import shutil
import tempfile
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from filepack.compressions.consts import (
    BZ2_SUFFIX,
    GZIP_SUFFIX,
    LZ4_SUFFIX,
    XZ_SUFFIX,
)
from filepack.compressions.exceptions import (
    FileAlreadyCompressed,
    FileNotCompressed,
)
from filepack.utils import get_file_type_extension


class CompressionType(Enum):
    """Enumeration for different compression types."""

    GZIP = GZIP_SUFFIX
    XZ = XZ_SUFFIX
    LZ4 = LZ4_SUFFIX
    BZ2 = BZ2_SUFFIX


class AbstractCompression(ABC):
    """Abstract base class for different compression types."""

    def __init__(self, path: Path, extension: str) -> None:
        """Initializes an AbstractCompression with the path to the file and its extension.

        Args:
            path: The filesystem path to the file.
            extension: The extension of the compressed file.
        """
        self._path = path
        self._suffix = path.suffix.lstrip(".")
        self._dot_suffix = path.suffix
        self._extension = extension

    def uncompressed_size(self) -> int:
        """Calculates the size of the uncompressed file.

        Returns:
            The size of the uncompressed file in bytes.
        """
        if not self.is_compressed():
            return self._path.stat().st_size

        with tempfile.NamedTemporaryFile() as temporary_file:
            self.decompress(target_path=temporary_file.name)
            return Path(temporary_file.name).stat().st_size

    def compressed_size(self, compression_level: int | None = None) -> int:
        """Calculates the size of the compressed file.

        Args:
            compression_level: The level of compression to use.

        Returns:
            The size of the compressed file in bytes.
        """
        if not self.is_compressed():
            if compression_level is None:
                raise ValueError(
                    (
                        "Failed to infer the compressed size "
                        "of an uncompressed file "
                        "- need compression level"
                    )
                )
            with tempfile.NamedTemporaryFile() as temporary_file:
                self.compress(
                    target_path=temporary_file.name,
                    compression_level=compression_level,
                )
                return Path(temporary_file.name).stat().st_size

        return self._path.stat().st_size

    def compression_ratio(self) -> str:
        """Calculates the compression ratio.

        Returns:
            The compression ratio as a string.
        """
        ratio = round(self.uncompressed_size() / self.compressed_size(), 2)
        return f"{ratio}:1"

    @abstractmethod
    def _open(
        self,
        file_path: str | Path,
        mode: str = "rb",
        compression_level: int = 9,
    ):
        """Opens the compression file with the given mode and compression level.

        Args:
            file_path: The path to the file.
            mode: The mode in which to open the file.
            compression_level: The level of compression.
        """
        pass

    def compress(
        self,
        target_path: str | Path | None = None,
        in_place: bool = False,
        compression_level: int = 9,
    ) -> Path:
        """Compresses the file.

        Args:
            target_path: The target path where the compressed file will be saved.
            in_place: If True, the file will be replaced with its new compression.
            compression_level: The level of compression to use.

        Returns:
            The path to the compressed file.
        """
        if self.is_compressed():
            raise FileAlreadyCompressed()

        if target_path is None:
            target_path = (
                self._path.parent / f"{self._path.name}.{self._extension}"
            )

        else:
            target_path = Path(target_path)

        with open(file=self._path, mode="rb") as uncompressed_file:
            with self._open(
                file_path=target_path,
                mode="wb",
                compression_level=compression_level,
            ) as compressed_file:
                shutil.copyfileobj(
                    fsrc=uncompressed_file, fdst=compressed_file
                )

            if in_place:
                os.remove(self._path)
                self._path = target_path

        return self._path

    def decompress(
        self, target_path: str | Path | None = None, in_place: bool = False
    ) -> Path:
        """Decompresses the file.

        Args:
            target_path: The target path where the decompressed file will be saved.
            in_place: If True, the file will be replaced with its new decompression.

        Returns:
            The path to the decompressed file.
        """
        if not self.is_compressed():
            raise FileNotCompressed()

        if target_path is None:
            target_path = self._path.parent / self._path.stem

        else:
            target_path = Path(target_path)

        with self._open(file_path=self._path, mode="rb") as compressed_file:
            with open(file=target_path, mode="wb") as decompressed_file:
                shutil.copyfileobj(
                    fsrc=compressed_file, fdst=decompressed_file
                )

        if in_place:
            os.remove(self._path)
            self._path = target_path

        return self._path

    def is_compressed(self) -> bool:
        """Checks if the file is compressed.

        Returns:
            True if the file is compressed, False otherwise.
        """
        try:
            return get_file_type_extension(self._path) == self._extension
        except ValueError:
            return False
