from pathlib import Path
from typing import Optional, final

from filepack.archives.exceptions import (
    FailedToAddNewMemberToArchive,
    FailedToExtractArchiveMember,
    FailedToExtractArchiveMembers,
    FailedToGetArchiveMember,
    FailedToGetArchiveMembers,
    FailedToRemoveArchiveMember,
    FailedToRemoveArchiveMembers,
)
from filepack.archives.models import (
    AbstractArchive,
    ArchiveMember,
    ArchiveType,
)
from filepack.archives.rar import RarArchive
from filepack.archives.seven_zip import SevenZipArchive
from filepack.archives.tar import TarArchive
from filepack.archives.zip import ZipArchive
from filepack.consts import ERROR_MESSAGE_NOT_SUPPORTED
from filepack.utils import get_file_type_extension, reraise_as


@final
class Archive:
    def __init__(self, path: Path) -> None:
        """Initializes the Archive object with a given path. It determines the archive type based on the file
        extension or magic numbers and creates an appropriate archive instance.

        Args:
            path: The file system path to the archive file.

        Raises:
            ValueError: If the archive type is not supported or cannot be determined.
        """
        self._path = Path(path)

        # if doesn't exist, try to infer the desired type from the extension
        if not self._path.exists():
            try:
                self._type = ArchiveType(self._path.suffix.lstrip("."))
            except Exception:
                raise ValueError(ERROR_MESSAGE_NOT_SUPPORTED)

        # if exist, get the type according to magic numbers
        else:
            self._type = ArchiveType(get_file_type_extension(path=self._path))

        self._instance: AbstractArchive

        match self._type:
            case ArchiveType.TAR:
                self._instance = TarArchive(
                    path=path,
                )

            case ArchiveType.ZIP:
                self._instance = ZipArchive(
                    path=path,
                )

            case ArchiveType.RAR:
                self._instance = RarArchive(
                    path=path,
                )

            case ArchiveType.SEVEN_ZIP:
                self._instance = SevenZipArchive(
                    path=path,
                )

            case _:
                raise ValueError(ERROR_MESSAGE_NOT_SUPPORTED)

    @property
    def path(self) -> Path:
        """The file path of the archive.

        Returns:
            The Path object representing the path of the archive file.
        """
        return self._path

    @property
    def suffix(self) -> str:
        """The file suffix (extension) of the archive.

        Returns:
            The file suffix as a string.
        """
        return self._type.value

    @reraise_as(FailedToExtractArchiveMember)
    def extract_member(self, member_name: str, target_path: str | Path):
        """Extracts a specific member from the archive to a given target path.

        Args:
            member_name: The name of the member to extract.
            target_path: The target directory path where the member will be extracted.

        Raises:
            FailedToExtractArchiveMember: If the member extraction fails.
        """
        self._instance.extract_member(
            member_name=member_name, target_path=Path(target_path)
        )

    @reraise_as(FailedToGetArchiveMembers)
    def get_members(self) -> list[ArchiveMember]:
        """Retrieves metadata for all members in the archive.

        Returns:
            A list of ArchiveMember objects representing the members of the archive.

        Raises:
            FailedToGetArchiveMembers: If the operation to get members fails.
        """
        return self._instance.get_members()

    @reraise_as(FailedToAddNewMemberToArchive)
    def add_member(self, member_path: str | Path, in_place: bool = False):
        """Adds a new member to the archive.

        Args:
            member_path: The file system path to the member to add.
            in_place: If true, the member's path will be deleted after addition.

        Raises:
            FailedToAddNewMemberToArchive: If adding the new member fails.
        """
        self._instance.add_member(
            member_path=Path(member_path), in_place=in_place
        )

    @reraise_as(FailedToRemoveArchiveMember)
    def remove_member(self, member_name: str):
        """Removes a member from the archive.

        Args:
            member_name: The name of the member to remove.

        Raises:
            FailedToRemoveArchiveMember: If the removal of the member fails.
        """
        self._instance.remove_member(member_name=member_name)

    @reraise_as(FailedToExtractArchiveMembers)
    def extract_all(self, target_path: str | Path, in_place: bool = False):
        """Extracts all members from the archive to the specified target path.

        Args:
            target_path: The target directory path where the members will be extracted.
            in_place: If True, extract all files and remove the archive.

        Raises:
            FailedToExtractArchiveMembers: If extracting all members fails.
        """
        self._instance.extract_all(
            target_path=Path(target_path), in_place=in_place
        )

    @reraise_as(FailedToRemoveArchiveMembers)
    def remove_all(self):
        """Removes all members from the archive.

        Raises:
            FailedToRemoveArchiveMembers: If removing all members fails.
        """
        self._instance.remove_all()

    @reraise_as(FailedToGetArchiveMember)
    def get_member(self, member_name: str) -> Optional[ArchiveMember]:
        """Retrieves metadata of a specific member in the archive.

        Args:
            member_name: The name of the member to retrieve metadata for.

        Returns:
            An ArchiveMember object if the member exists, None otherwise.

        Raises:
            FailedToGetArchiveMember: If retrieving the member metadata fails.
        """
        return self._instance.get_member(member_name=member_name)

    @reraise_as(FailedToGetArchiveMembers)
    def get_members_name(self) -> list[str]:
        """Retrieves the names of all members in the archive.

        Returns:
            A list of names of all members in the archive.

        Raises:
            FailedToGetArchiveMembers: If retrieving the members' names fails.
        """
        return self._instance.get_members_name()

    @reraise_as(FailedToGetArchiveMembers)
    def print_members(self):
        """Prints a tabulated view of all members in the archive and their metadata.

        Raises:
            FailedToGetArchiveMembers: If printing the members' information fails.
        """
        self._instance.print_members()
