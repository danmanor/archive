from pathlib import Path
from typing import Optional

from filepack.archive import Archive
from filepack.archives.models import ArchiveMember
from filepack.compression import Compression
from filepack.utils import ensure_instance


class FilePack:
    """Provides a unified interface for interacting with archive and compression operations."""

    def __init__(self, path: str | Path) -> None:
        """Initializes the FilePack with the specified file path. It attempts to create instances of
        Archive and Compression classes based on the file type.

        Args:
            path: The file system path to the file.
        """
        self._path = Path(path)

        try:
            self._archive_instance = Archive(path=self._path)
        except Exception:
            pass

        try:
            self._compression_instance = Compression(path=self._path)
        except Exception:
            pass

        if (
            getattr(self, "_archive_instance", None) is None
            and getattr(self, "_compression_instance", None) is None
        ):
            raise ValueError()

    @property
    def path(self) -> Path:
        """The path of the file associated with this FilePack instance.

        Returns:
            The Path object of the file.
        """
        return self._path

    @property
    def suffix(self) -> str:
        """The file suffix without the leading dot.

        Returns:
            The file suffix as a string.
        """
        return self.path.suffix.lstrip(".")

    @ensure_instance("_compression_instance")
    def uncompressed_size(self, compression_algorithm: str) -> int:
        """Returns the size of the uncompressed file
        for the specified compression algorithm.

        Args:
            compression_algorithm: The compression algorithm to use.

        Returns:
            The size of the uncompressed file in bytes.
        """
        return self._compression_instance.uncompressed_size(
            compression_algorithm=compression_algorithm
        )

    @ensure_instance("_compression_instance")
    def compressed_size(
        self, compression_algorithm: str, compression_level: int | None = None
    ) -> int:
        """Calculates the compressed size of the file,
        optionally with a specified compression level.

        Args:
            compression_algorithm: The algorithm used for compression.
            compression_level: The level of compression to apply.

        Returns:
            The size of the compressed file in bytes.
        """
        return self._compression_instance.compressed_size(
            compression_algorithm=compression_algorithm,
            compression_level=compression_level,
        )

    @ensure_instance("_compression_instance")
    def compression_ratio(self, compression_algorithm: str) -> str:
        """Calculates the compression ratio for the file.

        Args:
            compression_algorithm: The algorithm used for compression.

        Returns:
            A string representing the compression ratio.
        """
        return self._compression_instance.compression_ratio(
            compression_algorithm=compression_algorithm
        )

    @ensure_instance("_archive_instance")
    def extract_member(self, member_name: str, target_path: Path):
        """Extracts a specific member from an archive to a target path.

        Args:
            member_name: The name of the member to extract.
            target_path: The target directory path where the member will be extracted.
            in_place: If True, the member will be removed from archive after extraction.
        """
        self._archive_instance.extract_member(
            member_name=member_name, target_path=target_path
        )

    @ensure_instance("_archive_instance")
    def get_members(self) -> list[ArchiveMember]:
        """Retrieves metadata for all members in the archive.

        Returns:
            A list of ArchiveMember objects representing the members of the archive.
        """
        return self._archive_instance.get_members()

    @ensure_instance("_archive_instance")
    def add_member(self, member_path: str | Path, in_place: bool = False):
        """Adds a new member to the archive.

        Args:
            member_path: The file system path to the member to add.
            in_place: If true, the member's path will be deleted after addition.
        """
        self._archive_instance.add_member(
            member_path=member_path, in_place=in_place
        )

    @ensure_instance("_archive_instance")
    def remove_member(self, member_name: str):
        """Removes a member from the archive.

        Args:
            member_name: The name of the member to remove.
        """
        self._archive_instance.remove_member(member_name=member_name)

    @ensure_instance("_archive_instance")
    def extract_all(self, target_path: str | Path, in_place: bool = False):
        """Extracts all members from the archive to the specified target path.

        Args:
            target_path: The target directory path where the members will be extracted.
            in_place: If True, extract all files and remove archive.
        """
        self._archive_instance.extract_all(
            target_path=target_path, in_place=in_place
        )

    @ensure_instance("_archive_instance")
    def remove_all(self):
        """Removes all members from the archive."""
        self._archive_instance.remove_all()

    @ensure_instance("_archive_instance")
    def get_member(self, member_name: str) -> Optional[ArchiveMember]:
        """Retrieves metadata of a specific member in the archive.

        Args:
            member_name: The name of the member to retrieve metadata for.

        Returns:
            An ArchiveMember object if the member exists, None otherwise.
        """
        return self._archive_instance.get_member(member_name=member_name)

    @ensure_instance("_archive_instance")
    def get_members_name(self) -> list[str]:
        """Retrieves the names of all members in the archive.

        Returns:
            A list of names of all members in the archive.
        """
        return self._archive_instance.get_members_name()

    @ensure_instance("_archive_instance")
    def print_members(self):
        """Prints a tabulated view of all members in the archive and their metadata."""
        self._archive_instance.print_members()

    @ensure_instance("_compression_instance")
    def decompress(
        self,
        compression_algorithm: str,
        target_path: str | Path | None = None,
        in_place: bool = False,
    ):
        """Decompresses the file using the specified compression algorithm.

        Args:
            compression_algorithm: The algorithm used for decompression.
            target_path: The target path where the decompressed file will be saved.
            in_place: If True, the file will be replaced with its new decompression.

        Returns:
            The path to the decompressed file.
        """
        self._path = self._compression_instance.decompress(
            target_path=target_path,
            in_place=in_place,
            compression_algorithm=compression_algorithm,
        )

        return self._path

    @ensure_instance("_compression_instance")
    def compress(
        self,
        compression_algorithm: str,
        target_path: str | Path | None = None,
        in_place: bool = False,
        compression_level: int = 9,
    ):
        """Compresses the file using the specified compression algorithm.

        Args:
            compression_algorithm: The algorithm used for compression.
            target_path: The target path where the compressed file will be saved.
            in_place: If True, the file will be replaced with its new decompression.
            compression_level: The level of compression to apply.

        Returns:
            The path to the compressed file.
        """
        self._path = self._compression_instance.compress(
            target_path=target_path,
            in_place=in_place,
            compression_level=compression_level,
            compression_algorithm=compression_algorithm,
        )

        return self._path

    @ensure_instance("_compression_instance")
    def is_compressed(self, compression_algorithm: str) -> bool:
        """Checks if the file is compressed with the specified algorithm.

        Args:
            compression_algorithm: The algorithm to check against.

        Returns:
            True if the file is compressed with the specified algorithm, False otherwise.
        """
        return self._compression_instance.is_compressed(
            compression_algorithm=compression_algorithm
        )
