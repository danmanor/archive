import tempfile
from pathlib import Path
from typing import Optional

import py7zr

from filepack.archives.exceptions import ArchiveMemberDoesNotExist
from filepack.archives.models import (
    AbstractArchive,
    ArchiveMember,
    UnknownFileType,
)
from filepack.utils import get_file_type_extension


class SevenZipArchive(AbstractArchive):
    """Represents a 7z archive, providing methods to manipulate and retrieve information about its
    contents."""

    def __init__(
        self,
        path: Path,
    ):
        """Constructs a SevenZipArchive object associated with the given path.

        Args:     path: The filesystem path to the 7z archive.
        """
        self._path = path

    def extract_member(
        self, member_name: str, target_path: str | Path, in_place: bool = False
    ):
        """Extracts a specific member from the 7z archive.

        Args:
            member_name: The name of the member to extract.
            target_path: The filesystem path to extract the member to.
            in_place: If True, the member will be removed from archive after.

        Raises:
            ArchiveMemberDoesNotExist: If the specified member does not exist in the archive.
        """
        if not self.member_exist(member_name=member_name):
            raise ArchiveMemberDoesNotExist()

        with py7zr.SevenZipFile(file=self._path, mode="r") as seven_zip_file:
            seven_zip_file.extract(targets=[member_name], path=target_path)

        if in_place:
            self.remove_member(member_name=member_name)

    def get_member(self, member_name: str) -> Optional[ArchiveMember]:
        """Retrieves an archive member's metadata.

        Args:
            member_name: The name of the member to retrieve metadata for.

        Returns:
            The metadata of the member if found, None otherwise.
        """
        with py7zr.SevenZipFile(file=self._path, mode="r") as seven_zip_file:
            try:
                return self._seven_zip_info_to_archive_member(
                    [
                        member
                        for member in seven_zip_file.list()
                        if member.filename == member_name
                    ][0]
                )
            except IndexError:
                return None

    def get_members(self) -> list[ArchiveMember]:
        """Retrieves metadata for all members in the 7z archive.

        Returns:
            A list of ArchiveMember objects with metadata of all members.
        """
        with py7zr.SevenZipFile(file=self._path, mode="r") as seven_zip_file:
            return [
                self._seven_zip_info_to_archive_member(
                    seven_zip_info=seven_zip_info
                )
                for seven_zip_info in seven_zip_file.list()
            ]

    def add_member(self, member_path: str | Path, in_place: bool = False):
        """Adds a file to the 7z archive as a new member.

        Args:
            member_path: The filesystem path to the file to be added.
            in_place: If true, the member's path will be deleted after addition.

        Raises:
            FileNotFoundError: If the file at member_path does not exist.
        """
        member_path = Path(member_path)
        if not member_path.exists():
            raise FileNotFoundError()

        with py7zr.SevenZipFile(file=self._path, mode="a") as seven_zip_file:
            seven_zip_file.write(file=member_path, arcname=member_path.name)

        if in_place:
            member_path.unlink()

    def remove_member(self, member_name: str):
        """Removes a member from the 7z archive.

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
            with py7zr.SevenZipFile(
                file=new_archive_path, mode="w"
            ) as new_file:
                for file in temporary_directory_members_path.iterdir():
                    new_file.write(file=file, arcname=file.name)

            new_archive_path.rename(self._path)

    def member_exist(self, member_name: str) -> bool:
        """Checks if a specific member exists in the 7z archive.

        Args:
            member_name: The name of the member to check.

        Returns:
            True if the member exists, False otherwise.
        """
        with py7zr.SevenZipFile(file=self._path, mode="r") as seven_zip_file:
            return member_name in [
                seven_zip_info.filename
                for seven_zip_info in seven_zip_file.list()
            ]

    def _get_seven_zip_info_file_type(
        self, seven_zip_info: py7zr.FileInfo
    ) -> str | UnknownFileType:
        """Determines the file type of a 7z archive member based on its information.

        Args:
            seven_zip_info: The FileInfo object for the member.

        Returns:
            The file type if known, or an instance of UnknownFileType if not.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_file_path = (
                Path(temporary_directory) / seven_zip_info.filename
            )
            self.extract_member(
                member_name=seven_zip_info.filename,
                target_path=temporary_file_path,
            )

            try:
                type = get_file_type_extension(path=temporary_file_path)
                return type if type is not None else UnknownFileType()
            except Exception:
                return UnknownFileType()

    def _seven_zip_info_to_archive_member(
        self, seven_zip_info: py7zr.FileInfo
    ) -> ArchiveMember:
        """Converts FileInfo metadata to an ArchiveMember object.

        Args:
            seven_zip_info: The FileInfo object to convert.

        Returns:
            An object containing the member's metadata.
        """
        return ArchiveMember(
            name=seven_zip_info.filename,
            size=seven_zip_info.compressed,
            mtime=seven_zip_info.creationtime,
            type=self._get_seven_zip_info_file_type(
                seven_zip_info=seven_zip_info
            ),
        )
