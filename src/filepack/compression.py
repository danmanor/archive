from pathlib import Path
from typing import final

from filepack.compressions.bzip2 import BzipCompression
from filepack.compressions.exceptions import (
    CompressionTypeNotSupported,
    FailedToCompressFile,
    FailedToDecompressFile,
    FailedToGetCompressedSize,
    FailedToGetUncompressedSize,
)
from filepack.compressions.gzip import GzipCompression
from filepack.compressions.lz4 import LZ4Compression
from filepack.compressions.models import AbstractCompression, CompressionType
from filepack.compressions.xz import XZCompression
from filepack.utils import reraise_as


@final
class Compression:
    def __init__(self, path: Path) -> None:
        """
        Initializes the Compression object with a given file path. It checks if the file exists.

        Args:
            path: The file system path to the compressed or decompressible file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        self._path = Path(path)

        if not self._path.exists():
            raise FileNotFoundError()

    @property
    def path(self) -> Path:
        """The file path of the compressed or decompressible file.

        Returns:
            The Path object representing the file's path.
        """
        return self._path

    @property
    def suffix(self) -> str:
        """The file suffix (extension) of the compressed file.

        Returns:
            The file suffix as a string.
        """
        return self.path.suffix.lstrip(".")

    @reraise_as(FailedToGetUncompressedSize)
    def uncompressed_size(self, compression_algorithm: str) -> int:
        """Calculates the uncompressed size of the file for a specified compression algorithm.

        Args:
            compression_algorithm: The algorithm used for compression.

        Returns:
            The uncompressed size of the file in bytes.

        Raises:
            FailedToGetUncompressedSize: If the operation to get uncompressed size fails.
        """
        compression_instance = self._get_compression_instance(
            compression_algorithm=compression_algorithm
        )
        return compression_instance.uncompressed_size()

    @reraise_as(FailedToGetCompressedSize)
    def compressed_size(
        self, compression_algorithm: str, compression_level: int | None = None
    ) -> int:
        """Calculates the compressed size of the file, optionally with a specified compression level.

        Args:
            compression_algorithm: The algorithm used for compression.
            compression_level: The level of compression to apply, if applicable.

        Returns:
            The compressed size of the file in bytes.

        Raises:
            FailedToGetCompressedSize: If the operation to get compressed size fails.
        """
        compression_instance = self._get_compression_instance(
            compression_algorithm=compression_algorithm,
        )
        return compression_instance.compressed_size(
            compression_level=compression_level
        )

    def compression_ratio(self, compression_algorithm: str) -> str:
        """Calculates the compression ratio for the file using a specified compression algorithm.

        Args:
            compression_algorithm: The algorithm used for compression.

        Returns:
            A string representing the compression ratio.
        """
        compression_instance = self._get_compression_instance(
            compression_algorithm=compression_algorithm
        )
        return compression_instance.compression_ratio()

    @reraise_as(FailedToDecompressFile)
    def decompress(
        self,
        compression_algorithm: str,
        target_path: str | Path | None = None,
        in_place: bool = False,
    ) -> Path:
        """Decompresses the file using the specified compression algorithm.

        Args:
            compression_algorithm: The algorithm used for decompression.
            target_path: The target path where the decompressed file will be saved.
            in_place: If True, replaces the original file with the decompressed file.

        Returns:
            The path to the decompressed file.

        Raises:
            FailedToDecompressFile: If the decompression operation fails.
        """
        compression_instance = self._get_compression_instance(
            compression_algorithm=compression_algorithm
        )
        self._path = compression_instance.decompress(
            target_path=target_path, in_place=in_place
        )
        return self._path

    @reraise_as(FailedToCompressFile)
    def compress(
        self,
        compression_algorithm: str,
        target_path: str | Path | None = None,
        in_place: bool = False,
        compression_level: int = 9,
    ) -> Path:
        """Compresses the file using the specified compression algorithm.

        Args:
            compression_algorithm: The algorithm used for compression.
            target_path: The target path where the compressed file will be saved.
            in_place: If True, replaces the original file with the compressed file.
            compression_level: The level of compression to apply, if applicable.

        Returns:
            The path to the compressed file.

        Raises:
            FailedToCompressFile: If the compression operation fails.
        """
        compression_instance = self._get_compression_instance(
            compression_algorithm=compression_algorithm
        )
        self._path = compression_instance.compress(
            target_path=target_path,
            in_place=in_place,
            compression_level=compression_level,
        )
        return self._path

    def is_compressed(self, compression_algorithm: str) -> bool:
        """Checks if the file is compressed with the specified algorithm.

        Args:
            compression_algorithm: The algorithm to check against.

        Returns:
            True if the file is compressed with the specified algorithm, otherwise False.
        """
        compression_instance = self._get_compression_instance(
            compression_algorithm=compression_algorithm
        )
        return compression_instance.is_compressed()

    def _get_compression_instance(
        self, compression_algorithm: str
    ) -> AbstractCompression:
        """Creates an instance of the appropriate compression class based on the specified algorithm.

        Args:
            compression_algorithm: The algorithm used for compression or decompression.

        Returns:
            An instance of a subclass of AbstractCompression.

        Raises:
            CompressionTypeNotSupported: If the compression type is not supported.
        """
        try:
            match CompressionType(compression_algorithm):
                case CompressionType.GZIP:
                    return GzipCompression(
                        path=self.path,
                    )

                case CompressionType.BZ2:
                    return BzipCompression(
                        path=self.path,
                    )

                case CompressionType.LZ4:
                    return LZ4Compression(
                        path=self.path,
                    )

                case CompressionType.XZ:
                    return XZCompression(
                        path=self.path,
                    )
                case _:
                    raise CompressionTypeNotSupported()
        except Exception:
            raise CompressionTypeNotSupported()
