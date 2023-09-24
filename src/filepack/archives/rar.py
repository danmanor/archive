import tempfile
from pathlib import Path
from typing import Optional

import rarfile

from filepack.archives.exceptions import (
    ArchiveMemberDoesNotExist,
    FailedToAddNewMemberToArchive,
    FailedToRemoveArchiveMember,
)
from filepack.archives.models import (
    AbstractArchive,
    ArchiveMember,
    UnknownFileType,
)
from filepack.utils import format_date_tuple, get_file_type_extension


class RarArchive(AbstractArchive):
    """Represents a RAR archive, providing methods to manipulate and retrieve information about its
    contents."""

    def __init__(
        self,
        path: Path,
    ):
        """Constructs a RarArchive object associated with the given path.

        Args:
            path: The filesystem path to the RAR archive.
        """
        self._path = path

    def extract_member(
        self, member_name: str, target_path: str | Path, in_place: bool = False
    ):
        """Extracts a specific member from the RAR archive.

        Args:
            member_name: The name of the member to extract.
            target_path: The filesystem path to extract the member to.
            in_place: If True, the member will be removed from archive after

        Raises:
            ArchiveMemberDoesNotExist: If the specified member does not exist in the archive.
        """
        if not self.member_exist(member_name=member_name):
            raise ArchiveMemberDoesNotExist()

        with rarfile.RarFile(file=self._path, mode="r") as rar_file:
            rar_file.extract(member=member_name, path=target_path)

        if in_place:
            self.remove_member(member_name=member_name)

    def get_member(self, member_name: str) -> Optional[ArchiveMember]:
        """Retrieves an archive member's metadata.

        Args:
            member_name: The name of the member to retrieve metadata for.

        Returns:
            The metadata of the member if found, None otherwise.
        """
        with rarfile.RarFile(file=self._path, mode="r") as rar_file:
            try:
                return self._rar_info_to_archive_member(
                    rar_file.getinfo(name=member_name)
                )
            except rarfile.NoRarEntry:
                return None

    def get_members(self) -> list[ArchiveMember]:
        """Retrieves metadata for all members in the RAR archive.

        Returns:
            A list of ArchiveMember objects with metadata of all members.
        """
        with rarfile.RarFile(file=self._path, mode="r") as rar_file:
            return [
                self._rar_info_to_archive_member(rar_info=rar_info)
                for rar_info in rar_file.infolist()
            ]

    def add_member(self, member_path: str | Path, in_place: bool = False):
        """Raises an exception as RAR archives do not support adding members.

        Args:
            member_path: The filesystem path to the file to be added.
            in_place: If true, the member's path will be deleted after addition.

        Raises:
            FailedToAddNewMemberToArchive: Always.
        """
        raise FailedToAddNewMemberToArchive(
            "rar files does not support adding members"
        )

    def remove_member(self, member_name: str):
        """Raises an exception as RAR archives do not support removing members.

        Args:
            member_name: The name of the member to remove.

        Raises:
            FailedToRemoveArchiveMember: Always.
        """
        raise FailedToRemoveArchiveMember(
            "rar files does not support removing members"
        )

    def member_exist(self, member_name: str) -> bool:
        """Checks if a specific member exists in the RAR archive.

        Args:     member_name: The name of the member to check.

        Returns:     True if the member exists, False otherwise.
        """
        with rarfile.RarFile(file=self._path, mode="r") as rar_file:
            return member_name in [
                rar_info.filename for rar_info in rar_file.infolist()
            ]

    def _get_rar_info_file_type(
        self, rar_info: rarfile.RarInfo
    ) -> str | UnknownFileType:
        """Determines the file type of a RAR archive member based on its information.

        Args:
            rar_info: The RarInfo object for the member.

        Returns:
            The file type if known, or an instance of UnknownFileType if not.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_file_path = Path(temporary_directory) / rar_info.filename
            self.extract_member(
                member_name=rar_info.filename,
                target_path=temporary_file_path,
            )

            try:
                type = get_file_type_extension(path=temporary_file_path)
                return type if type is not None else UnknownFileType()
            except Exception:
                return UnknownFileType()

    def _rar_info_to_archive_member(
        self, rar_info: rarfile.RarInfo
    ) -> ArchiveMember:
        """Converts RarInfo metadata to an ArchiveMember object.

        Args:
            rar_info: The RarInfo object to convert.

        Returns:
            An object containing the member's metadata.
        """
        return ArchiveMember(
            name=rar_info.filename,
            size=rar_info.file_size,
            mtime=format_date_tuple(rar_info.date_time),
            type=self._get_rar_info_file_type(rar_info=rar_info),
        )
