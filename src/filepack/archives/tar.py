import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from filepack.archives.exceptions import ArchiveMemberDoesNotExist
from filepack.archives.models import (
    AbstractArchive,
    ArchiveMember,
    UnknownFileType,
)
from filepack.utils import get_file_type_extension


class TarArchive(AbstractArchive):
    """Represents a TAR archive, providing methods to manipulate and retrieve information about its
    contents."""

    def __init__(
        self,
        path: Path,
    ):
        """Represents a TAR archive, providing methods to manipulate and retrieve information about
        its contents."""
        self._path = path

    def extract_member(
        self, member_name: str, target_path: str | Path, in_place: bool = False
    ):
        """Extracts a specific member from the TAR archive.

        Args:
            member_name: The name of the member to extract.
            target_path: The filesystem path to extract the member to.
            in_place: If True, the member will be removed from archive after extraction.

        Raises:
            ArchiveMemberDoesNotExist: If the specified member does not exist in the archive.
        """
        if not self.member_exist(member_name=member_name):
            raise ArchiveMemberDoesNotExist()

        with tarfile.open(self._path, "r") as tar_file:
            tar_file.extract(member=member_name, path=target_path)

        if in_place:
            self.remove_member(member_name=member_name)

    def get_member(self, member_name: str) -> Optional[ArchiveMember]:
        """Retrieves an archive member's metadata.

        Args:
            member_name: The name of the member to retrieve metadata for.

        Returns:
            The metadata of the member if found, None otherwise.
        """
        with tarfile.open(name=self._path, mode="r") as tar_file:
            try:
                return self._tar_info_to_archive_member(
                    tar_file.getmember(name=member_name)
                )
            except KeyError:
                return None

    def get_members(self) -> list[ArchiveMember]:
        """Retrieves metadata for all members in the TAR archive.

        Returns:
            A list of ArchiveMember objects with metadata of all members.
        """
        with tarfile.open(self._path, "r") as tar_file:
            return [
                self._tar_info_to_archive_member(tar_info=tar_info)
                for tar_info in tar_file.getmembers()
            ]

    def add_member(self, member_path: str | Path, in_place: bool = False):
        """Adds a file to the TAR archive as a new member.

        Args:
            member_path: The filesystem path to the file to be added.
            in_place: If true, the member's path will be deleted after addition.

        Raises:
            FileNotFoundError: If the file at member_path does not exist.
        """
        member_path = Path(member_path)
        if not member_path.exists():
            raise FileNotFoundError()

        with tarfile.open(self._path, "a") as tar_file:
            tar_file.add(name=member_path, arcname=member_path.name)

        if in_place:
            member_path.unlink()

    def remove_member(self, member_name: str):
        """Removes a member from the TAR archive.

        Args:
            member_name: The name of the member to remove.

        Raises:
            ArchiveMemberDoesNotExist: If the specified member does not exist in the archive.
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
                    self.extract_member(
                        member_name=member.name,
                        target_path=temporary_directory_members_path,
                    )

            new_archive_path = Path(temporary_directory) / "new_archive"

            with tarfile.open(new_archive_path, "w") as new_file:
                for file in temporary_directory_members_path.iterdir():
                    new_file.add(name=file, arcname=file.name)

            new_archive_path.rename(self._path)

    def member_exist(self, member_name: str) -> bool:
        """Checks if a specific member exists in the TAR archive.

        Args:
            member_name: The name of the member to check.

        Returns:
            True if the member exists, False otherwise.
        """
        with tarfile.open(self._path, "r") as tar_file:
            return member_name in [
                tar_info.name for tar_info in tar_file.getmembers()
            ]

    def _get_tar_info_file_type(
        self, tar_info: tarfile.TarInfo
    ) -> str | UnknownFileType:
        """Determines the file type of a TAR archive member based on its information.

        Args:
            tar_info: The TarInfo object for the member.

        Returns:
            The file type as a string if known, or an instance of UnknownFileType if not.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_file_path = Path(temporary_directory) / tar_info.name
            self.extract_member(
                member_name=tar_info.name,
                target_path=temporary_file_path,
            )

            try:
                type = get_file_type_extension(path=temporary_file_path)
                return type if type is not None else UnknownFileType()
            except Exception:
                return UnknownFileType()

    def _tar_info_to_archive_member(
        self, tar_info: tarfile.TarInfo
    ) -> ArchiveMember:
        """Converts TarInfo metadata to an ArchiveMember object.

        Args:
            tar_info: The TarInfo object to convert.

        Returns:
            An object containing the member's metadata.
        """
        return ArchiveMember(
            name=tar_info.name,
            size=tar_info.size,
            mtime=datetime.utcfromtimestamp(tar_info.mtime).strftime(
                "%a, %d %b %Y %H:%M:%S UTC"
            ),
            type=self._get_tar_info_file_type(tar_info=tar_info),
        )
