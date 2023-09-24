from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Optional

from tabulate import tabulate

from filepack.archives.consts import (
    RAR_SUFFIX,
    SEVEN_ZIP_SUFFIX,
    TAR_SUFFIX,
    ZIP_SUFFIX,
)


class ArchiveType(Enum):
    """Enumeration for different archive types."""

    TAR = TAR_SUFFIX
    ZIP = ZIP_SUFFIX
    RAR = RAR_SUFFIX
    SEVEN_ZIP = SEVEN_ZIP_SUFFIX


class UnknownFileType:
    """Represents an unknown file type within an archive."""

    pass


class ArchiveMember:
    """Represents a single member within an archive, holding its metadata."""

    def __init__(
        self,
        name: str,
        size: int,
        mtime: str,
        type: str | UnknownFileType,
    ) -> None:
        """Initializes an ArchiveMember object with metadata.

        Args:
            name: The name of the archive member.
            size: The size of the archive member in bytes.
            mtime: The modification time of the archive member.
            type: The type of the file or an instance of UnknownFileType if unknown.
        """
        self.name = name
        self.size = size
        self.mtime = mtime
        self.type = type


class AbstractArchive(ABC):
    """Abstract base class for different archive types."""

    def __init__(self, path: Path, extension: str) -> None:
        """Initializes an AbstractArchive with the path to the archive and its extension.

        Args:
            path: The filesystem path to the archive.
            extension: The extension of the archive file.
        """
        self._path = path
        self._suffix = path.suffix.lstrip(".")
        self._dot_suffix = path.suffix
        self._extension = extension

    @abstractmethod
    def get_members(self) -> list[ArchiveMember]:
        """Retrieves a list of ArchiveMember objects representing the contents of the archive."""
        pass

    @abstractmethod
    def add_member(self, member_path: str | Path, in_place: bool = False):
        """Adds a new member to the archive.

        Args:
            member_path: The filesystem path of the member to add.
            in_place: If true, the member's path will be deleted after addition.
        """
        pass

    @abstractmethod
    def remove_member(self, member_name: str):
        """Removes a member from the archive.

        Args:
            member_name: The name of the member to remove.
        """
        pass

    @abstractmethod
    def get_member(self, member_name: str) -> Optional[ArchiveMember]:
        """Retrieves metadata for a specific member in the archive.

        Args:
            member_name: The name of the member to retrieve metadata for.

        Returns:
            An ArchiveMember object if the member exists, None otherwise.
        """
        pass

    @abstractmethod
    def member_exist(self, member_name: str) -> bool:
        """Checks whether a member exists in the archive.

        Args:
            member_name: The name of the member to check for existence.

        Returns:
            True if the member exists, False otherwise.
        """
        pass

    @abstractmethod
    def extract_member(
        self, member_name: str, target_path: str | Path, in_place: bool = False
    ):
        """Extracts a specific member from the archive to a target path.

        Args:
            member_name: The name of the member to extract.
            target_path: The target path where the member will be extracted.
            in_place: If True, the member will be removed from archive after extraction.
        """
        pass

    def extract_all(self, target_path: str | Path, in_place: bool = False):
        """Extracts all members from the archive to a target path.

        Args:
            target_path: The target path where the members will be
            in_place: If True, extract all files and remove archive. extracted.
        """
        for member in self.get_members():
            self.extract_member(
                member_name=member.name, target_path=target_path
            )

        if in_place:
            self._path.unlink()

    def remove_all(self):
        """Removes all members from the archive."""
        for member_name in self.get_members_name():
            self.remove_member(member_name=member_name)

    def get_members_name(self) -> list[str]:
        """Retrieves a list of names of all members in the archive.

        Returns:
            A list of member names.
        """
        return [member.name for member in self.get_members()]

    def print_members(self):
        """Prints a tabulated view of all members and their metadata."""
        members_metadata = [
            {
                "name": member.name,
                "mtime": member.mtime,
                "size": member.size,
                "type": member.type,
            }
            for member in self.get_members()
        ]
        print(tabulate(members_metadata, headers="keys", tablefmt="grid"))
