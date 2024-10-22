import tempfile
from pathlib import Path
from typing import Optional

from tabulate import tabulate

from filepack.archives.exceptions import (
    ArchiveMemberDoesNotExist,
    FailedToAddNewMemberToArchive,
    FailedToExtractArchiveMember,
    FailedToExtractArchiveMembers,
    FailedToGetArchiveMember,
    FailedToGetArchiveMembers,
    FailedToRemoveArchiveMember,
    FailedToRemoveArchiveMembers,
)
from filepack.archives.models import (
    AbsractArchiveClient,
    AbstractArchiveMember,
    ArchiveType,
)
from filepack.archives.seven_zip import SevenZipClient
from filepack.archives.tar import TarClient
from filepack.archives.zip import ZipClient
from filepack.consts import ERROR_MESSAGE_NOT_SUPPORTED
from filepack.utils import get_file_type_extension, reraise_as


class Archive:
    def __init__(self, path: str | Path) -> None:
        """
        Initializes the Archive class based on the provided path.

        Args:
            path: The path to the archive file.

        Raises:
            ValueError: If the archive type is unsupported.
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

        self._client: AbsractArchiveClient

        match self._type:
            case ArchiveType.TAR:
                self._client = TarClient()

            case ArchiveType.ZIP:
                self._client = ZipClient()

            case ArchiveType.SEVEN_ZIP:
                self._client = SevenZipClient()

            case _:
                raise ValueError(ERROR_MESSAGE_NOT_SUPPORTED)

    @property
    def path(self) -> Path:
        """
        Returns the path of the archive.

        Returns:
            The archive file path.
        """
        return self._path

    @property
    def size(self) -> int:
        """
        Returns the size of the archive in bytes.

        Returns:
            The size of the archive in bytes. Returns 0 if the path does not exist.
        """
        if not self.path_exists():
            return 0

        return self._path.stat().st_size

    def path_exists(self):
        """
        Checks if the archive path exists.

        Returns:
            True if the path exists, otherwise False.
        """
        return self._path.exists()

    def member_exist(self, member_name: str) -> bool:
        """
        Checks if a member exists within the archive.

        Args:
            member_name: The name of the archive member to check.

        Returns:
            True if the member exists, otherwise False.
        """
        return self.get_member(member_name=member_name) is not None

    @reraise_as(FailedToGetArchiveMembers)
    def get_members(self) -> list[AbstractArchiveMember]:
        """
        Retrieves all members from the archive.

        Returns:
            A list of archive members, or an empty list if the path does not exist.

        Raises:
            FailedToGetArchiveMembers: If there's an issue retrieving the archive members.
        """
        if not self.path_exists():
            return []

        with self._client.open(
            file_path=self._path, mode="r"
        ) as archive_object:
            return [
                archive_object
                for archive_object in archive_object.get_members()
            ]

    @reraise_as(FailedToGetArchiveMember)
    def get_member(self, member_name: str) -> Optional[AbstractArchiveMember]:
        """
        Retrieves a specific member from the archive.

        Args:
            member_name: The name of the archive member to retrieve.

        Returns:
            The archive member if found, otherwise None.

        Raises:
            FailedToGetArchiveMember: If there's an issue retrieving the member.
        """
        if not self.path_exists():
            return None

        with self._client.open(
            file_path=self._path, mode="r"
        ) as archive_object:
            return archive_object.get_member(member_name=member_name)

    @reraise_as(FailedToExtractArchiveMembers)
    def extract_all(
        self, target_directory_path: str | Path, in_place: bool = False
    ):
        """
        Extracts all members from the archive to a target directory.

        Args:
            target_directory_path: The directory path to extract the archive members to.
            in_place: If True, deletes the archive after extraction.

        Raises:
            FailedToExtractArchiveMembers: If there's an issue extracting the archive members.
        """
        if self.get_members() == []:
            return

        with self._client.open(self._path, "r") as archive_object:
            archive_object.extract_all(
                target_directory_path=Path(target_directory_path)
            )

        if in_place:
            self._path.unlink()

    @reraise_as(FailedToExtractArchiveMember)
    def extract_member(
        self,
        member_name: str,
        target_directory_path: str | Path,
        in_place: bool = False,
    ):
        """
        Extracts a specific member from the archive to a target directory.

        Args:
            member_name: The name of the archive member to extract.
            target_directory_path: The path to extract the archive member to.
            in_place: If True, deletes the archive member after extraction.

        Raises:
            FailedToExtractArchiveMember: If there's an issue extracting the archive member.
        """
        if self.get_member(member_name=member_name) is None:
            raise ArchiveMemberDoesNotExist()

        with self._client.open(self._path, "r") as archive_object:
            archive_object.extract_member(
                member_name=member_name,
                target_directory_path=Path(target_directory_path),
            )

        if in_place:
            self.remove_member(member_name=member_name)

    @reraise_as(FailedToAddNewMemberToArchive)
    def add_member(self, member_path: str | Path, in_place: bool = False):
        """
        Adds a new member to the archive.

        Args:
            member_path: The path to the file to be added to the archive.
            in_place: If True, deletes the file after adding it to the archive.

        Raises:
            FailedToAddNewMemberToArchive: If there's an issue adding the new member to the archive.
        """
        member_path = Path(member_path)

        if not member_path.exists():
            raise FileNotFoundError()

        with self._client.open(self._path, "a") as archive_object:
            archive_object.add_member(member_path=member_path)

        if in_place:
            member_path.unlink()

    @reraise_as(FailedToRemoveArchiveMember)
    def remove_member(self, member_name: str):
        """
        Removes a specific member from the archive.

        Args:
            member_name: The name of the archive member to remove.

        Raises:
            FailedToRemoveArchiveMember: If there's an issue removing the archive member.
        """
        if not self.member_exist(member_name=member_name):
            raise ArchiveMemberDoesNotExist()

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_directory_members_path = (
                Path(temporary_directory) / "files"
            )
            temporary_directory_members_path.mkdir()

            for member in self.get_members():
                if not member.name == member_name:
                    with self._client.open(self._path, "r") as archive_object:
                        archive_object.extract_member(
                            member_name=member.name,
                            target_directory_path=temporary_directory_members_path,
                        )

            new_archive_path = Path(temporary_directory) / "new_archive"

            with self._client.open(new_archive_path, "w") as new_file:
                for file in temporary_directory_members_path.iterdir():
                    new_file.add_member(member_path=file)

            new_archive_path.rename(self._path)

    @reraise_as(FailedToRemoveArchiveMembers)
    def remove_all(self):
        """
        Removes all members from the archive by deleting the archive file.

        Raises:
            FailedToRemoveArchiveMembers: If there's an issue removing the archive members.
        """
        if not self.path_exists():
            return None

        self._path.unlink()

    def print_members(self):
        """
        Prints the metadata of all members in the archive in a tabular format.
        """
        members_metadata = [
            {
                "name": member.name,
                "mtime": member.mtime,
                "size": str(member.size) + "B",
                "type": member.type,
            }
            for member in self.get_members()
        ]
        print(tabulate(members_metadata, headers="keys", tablefmt="grid"))
