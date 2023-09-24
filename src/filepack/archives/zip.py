import tempfile
import zipfile
from pathlib import Path
from typing import Optional

from filepack.archives.exceptions import ArchiveMemberDoesNotExist
from filepack.archives.models import (
    AbstractArchive,
    ArchiveMember,
    UnknownFileType,
)
from filepack.utils import format_date_tuple, get_file_type_extension


class ZipArchive(AbstractArchive):
    """Represents a ZIP archive, providing methods to manipulate and retrieve information about its
    contents."""

    def __init__(
        self,
        path: Path,
    ):
        """Constructs a ZipArchive object associated with the given path.

        Args:
            path: The filesystem path to the ZIP archive.
        """
        self._path = path

    def extract_member(
        self, member_name: str, target_path: str | Path, in_place: bool = False
    ):
        """Extracts a specific member from the ZIP archive.

        Args:
            member_name: The name of the member to extract.
            target_path: The filesystem path to extract the member to.
            in_place: If True, the member will be removed from archive after extraction.

        Raises:
            ArchiveMemberDoesNotExist: If the specified member does not exist in the archive.
        """
        if not self.member_exist(member_name=member_name):
            raise ArchiveMemberDoesNotExist()

        with zipfile.ZipFile(file=self._path, mode="r") as zip_file:
            zip_file.extract(member=member_name, path=target_path)

        if in_place:
            self.remove_member(member_name=member_name)

    def get_member(self, member_name: str) -> Optional[ArchiveMember]:
        """Retrieves an archive member's metadata.

        Args:
            member_name: The name of the member to retrieve metadata for.

        Returns:
            The metadata of the member if found, None otherwise.
        """
        with zipfile.ZipFile(file=self._path, mode="r") as zip_file:
            try:
                return self._zip_info_to_archive_member(
                    zip_info=zip_file.getinfo(name=member_name)
                )
            except KeyError:
                return None

    def get_members(self) -> list[ArchiveMember]:
        """Retrieves metadata for all members in the ZIP archive.

        Returns:
            A list of ArchiveMember objects with metadata of all members.
        """
        with zipfile.ZipFile(file=self._path, mode="r") as zip_file:
            return [
                self._zip_info_to_archive_member(zip_info=zip_info)
                for zip_info in zip_file.infolist()
            ]

    def add_member(self, member_path: str | Path, in_place: bool = False):
        """Adds a file to the ZIP archive as a new member.

        Args:
            member_path: The filesystem path to the file to be added.
            in_place: If true, the member's path will be deleted after addition.

        Raises:
            FileNotFoundError: If the file at member_path does not exist.
        """
        member_path = Path(member_path)
        if not member_path.exists():
            raise FileNotFoundError()

        with zipfile.ZipFile(file=self._path, mode="a") as zip_file:
            zip_file.write(
                filename=member_path, arcname=Path(member_path).name
            )

        if in_place:
            member_path.unlink()

    def remove_member(self, member_name: str):
        """Removes a member from the ZIP archive.

        Args:
            member_name: The name of the member to remove.

        Raises:
            ArchiveMemberDoesNotExist: If the specified member does not exist in the archive.
        """
        if not self.member_exist(member_name):
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

            with zipfile.ZipFile(new_archive_path, "w") as new_file:
                for file in temporary_directory_members_path.iterdir():
                    new_file.write(filename=file, arcname=file.name)

            new_archive_path.rename(self._path)

    def member_exist(self, member_name: str) -> bool:
        """Checks if a specific member exists in the ZIP archive.

        Args:
            member_name: The name of the member to check.

        Returns:
            True if the member exists, False otherwise.
        """
        with zipfile.ZipFile(file=self._path, mode="r") as zip_file:
            return member_name in [
                zip_info.filename for zip_info in zip_file.infolist()
            ]

    def _get_zip_info_file_type(
        self, zip_info: zipfile.ZipInfo
    ) -> str | UnknownFileType:
        """Determines the file type of a ZIP archive member based on its information.

        Args:
            zip_info: The ZipInfo object for the member.

        Returns:
            The file type if known, or an instance of UnknownFileType if not.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_file_path = Path(temporary_directory) / zip_info.filename
            self.extract_member(
                member_name=zip_info.filename,
                target_path=temporary_file_path,
            )

            try:
                type = get_file_type_extension(path=temporary_file_path)
                return type if type is not None else UnknownFileType()
            except Exception:
                return UnknownFileType()

    def _zip_info_to_archive_member(
        self, zip_info: zipfile.ZipInfo
    ) -> ArchiveMember:
        """Converts ZipInfo metadata to an ArchiveMember object.

        Args:
            zip_info: The ZipInfo object to convert.

        Returns:
            An object containing the member's metadata.
        """
        return ArchiveMember(
            name=zip_info.filename,
            size=zip_info.file_size,
            mtime=format_date_tuple(zip_info.date_time),
            type=self._get_zip_info_file_type(zip_info=zip_info),
        )
