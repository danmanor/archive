import os
import shutil
import tempfile
from pathlib import Path

from filepack.compressions.bzip2 import BzipCompression
from filepack.compressions.exceptions import (
    CompressionTypeNotSupported,
    FailedToCompressFile,
    FailedToDecompressFile,
    FailedToGetCompressedSize,
    FailedToGetUncompressedSize,
    FileAlreadyCompressed,
    FileNotCompressed,
)
from filepack.compressions.gzip import GzipCompression
from filepack.compressions.lz4 import LZ4Compression
from filepack.compressions.models import AbstractCompression, CompressionType
from filepack.compressions.xz import XZCompression
from filepack.utils import get_file_type_extension, reraise_as


class Compression:
    def __init__(self, path: str | Path) -> None:
        """
        Initializes the Compression class based on the provided file path.

        Args:
            path: The path to the file to be compressed or decompressed.

        Raises:
            FileNotFoundError: If the provided path does not exist.
        """
        self._path = Path(path)

        if not self._path.exists():
            raise FileNotFoundError()

    @property
    def path(self) -> Path:
        """
        Returns the file path.

        Returns:
            The path of the file.
        """
        return self._path

    @reraise_as(FailedToGetUncompressedSize)
    def uncompressed_size(self, compression_algorithm: str) -> int:
        """
        Returns the uncompressed size of the file, based on the specified compression algorithm.

        Args:
            compression_algorithm: The algorithm used for compression.

        Returns:
            The uncompressed file size in bytes.

        Raises:
            FailedToGetUncompressedSize: If there's an error while retrieving the uncompressed size.
        """
        if not self.is_compressed(compression_algorithm=compression_algorithm):
            return self._path.stat().st_size

        with tempfile.NamedTemporaryFile() as temporary_file:
            self.decompress(
                target_path=temporary_file.name,
                compression_algorithm=compression_algorithm,
            )
            return Path(temporary_file.name).stat().st_size

    @reraise_as(FailedToGetCompressedSize)
    def compressed_size(
        self, compression_algorithm: str, compression_level: int | None = None
    ) -> int:
        """
        Returns the compressed size of the file, based on the specified compression algorithm.

        Args:
            compression_algorithm: The algorithm used for compression.
            compression_level: The level of compression to apply if compressing the file.

        Returns:
            The compressed file size in bytes.

        Raises:
            FailedToGetCompressedSize: If there's an error while retrieving the compressed size.
        """
        if self.is_compressed(compression_algorithm=compression_algorithm):
            return self._path.stat().st_size

        if compression_level is None:
            raise ValueError(
                "compression_level is manadatory for calculating compressed file size"
            )

        with tempfile.NamedTemporaryFile() as temporary_file:
            self.compress(
                target_path=temporary_file.name,
                compression_algorithm=compression_algorithm,
                compression_level=compression_level,
            )
            return Path(temporary_file.name).stat().st_size

    def compression_ratio(self, compression_algorithm: str) -> str:
        """
        Returns the compression ratio for the file using the specified algorithm.

        Args:
            compression_algorithm: The algorithm used for compression.

        Returns:
            A string representing the compression ratio (e.g., "2.5:1").
        """
        ratio = round(
            self.uncompressed_size(compression_algorithm=compression_algorithm)
            / self.compressed_size(
                compression_algorithm=compression_algorithm,
            ),
            2,
        )
        return f"{ratio}:1"

    @reraise_as(FailedToDecompressFile)
    def decompress(
        self,
        compression_algorithm: str,
        target_path: str | Path | None = None,
        in_place: bool = False,
    ) -> Path:
        """
        Decompresses the file using the specified compression algorithm.

        Args:
            compression_algorithm: The algorithm used to decompress the file.
            target_path: The path where the decompressed file will be saved. If None, uses the same directory.
            in_place: If True, replaces the compressed file with the decompressed file.

        Returns:
            The path to the decompressed file.

        Raises:
            FailedToDecompressFile: If there's an error during decompression.
        """
        if not self.is_compressed(compression_algorithm=compression_algorithm):
            raise FileNotCompressed()

        if target_path is None:
            target_path = self._path.parent / self._path.stem
        else:
            target_path = Path(target_path)

        compression_client = self._get_compression_client(
            compression_algorithm=compression_algorithm
        )

        with compression_client.open(
            file_path=self._path, mode="r"
        ) as compression_object:
            with open(file=target_path, mode="wb") as target_file:
                shutil.copyfileobj(fsrc=compression_object, fdst=target_file)

        if in_place:
            self._path.unlink()
            self._path = target_path

        return self._path

    @reraise_as(FailedToCompressFile)
    def compress(
        self,
        compression_algorithm: str,
        target_path: str | Path | None = None,
        in_place: bool = False,
        compression_level: int = 9,
    ) -> Path:
        """
        Compresses the file using the specified algorithm and compression level.

        Args:
            compression_algorithm: The algorithm used for compression.
            target_path: The path where the compressed file will be saved. If None, adds the algorithm as a suffix.
            in_place: If True, replaces the original file with the compressed version.
            compression_level: The level of compression to apply, where 9 is maximum compression.

        Returns:
            The path to the compressed file.

        Raises:
            FailedToCompressFile: If there's an error during compression.
        """
        if self.is_compressed(compression_algorithm=compression_algorithm):
            raise FileAlreadyCompressed()

        if target_path is None:
            target_path = (
                self._path.parent
                / f"{self._path.name}.{compression_algorithm}"
            )

        else:
            target_path = Path(target_path)

        compression_client = self._get_compression_client(
            compression_algorithm=compression_algorithm
        )

        with open(file=self._path, mode="rb") as uncompressed_file:
            with compression_client.open(
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

    def is_compressed(self, compression_algorithm: str) -> bool:
        """
        Checks if the file is compressed using the specified algorithm.

        Args:
            compression_algorithm: The algorithm to check.

        Returns:
            True if the file is compressed with the specified algorithm, otherwise False.
        """
        try:
            return get_file_type_extension(self._path) == compression_algorithm
        except ValueError:
            return False

    def _get_compression_client(
        self, compression_algorithm: str
    ) -> AbstractCompression:
        try:
            match CompressionType(compression_algorithm):
                case CompressionType.GZIP:
                    return GzipCompression()

                case CompressionType.BZ2:
                    return BzipCompression()

                case CompressionType.LZ4:
                    return LZ4Compression()

                case CompressionType.XZ:
                    return XZCompression()
                case _:
                    raise CompressionTypeNotSupported()
        except Exception:
            raise CompressionTypeNotSupported()
