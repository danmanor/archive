import tempfile
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Optional

from filepack.archives.consts import SEVEN_ZIP_SUFFIX, TAR_SUFFIX, ZIP_SUFFIX
from filepack.archives.types import ArchiveObjectTypes
from filepack.utils import get_file_type_extension


class ArchiveType(Enum):
    """Enumeration for different archive types."""

    TAR = TAR_SUFFIX
    ZIP = ZIP_SUFFIX
    SEVEN_ZIP = SEVEN_ZIP_SUFFIX


class UnknownFileType:
    """Represents an unknown file type within an archive."""

    def __str__(self) -> str:
        return "Unknown File Type"


class AbstractArchiveObject(ABC):
    def __init__(
        self,
        archive_object: ArchiveObjectTypes,
        client: "AbsractArchiveClient",
        path: Path,
    ) -> None:
        self._archive_object = archive_object
        self._client = client
        self._path = path

    def __enter__(self) -> "AbstractArchiveObject":
        self._archive_object = self._archive_object.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._archive_object.__exit__(exc_type, exc_value, traceback)

    def extract_all(self, target_directory_path: Path):
        for member in self.get_members():
            self.extract_member(
                member_name=member.name,
                target_directory_path=target_directory_path,
            )

    def get_member(
        self, member_name: str
    ) -> Optional["AbstractArchiveMember"]:
        try:
            return next(
                member
                for member in self.get_members()
                if member.name == member_name
            )
        except StopIteration:
            return None

    @abstractmethod
    def get_members(self) -> list["AbstractArchiveMember"]:
        pass

    @abstractmethod
    def extract_member(self, member_name: str, target_directory_path: Path):
        pass

    @abstractmethod
    def add_member(self, member_path: Path):
        pass


class AbsractArchiveClient(ABC):
    @abstractmethod
    def open(self, file_path: Path, mode: str) -> AbstractArchiveObject:
        pass


class AbstractArchiveMember(ABC):
    def __init__(
        self,
        client: AbsractArchiveClient,
        archive_path: Path,
        name: str,
        size: int,
        mtime: str,
    ) -> None:
        self._client = client
        self._archive_path = archive_path
        self._name = name
        self._size = size
        self._mtime = mtime

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return self._size

    @property
    def mtime(self) -> str:
        return self._mtime

    @property
    def type(self) -> str:
        with self._client.open(self._archive_path, "r") as archive_object:
            with tempfile.TemporaryDirectory() as temporary_directory:
                temporary_directory_path = (
                    Path(temporary_directory) / self._name
                )
                archive_object.extract_member(
                    member_name=self._name,
                    target_directory_path=temporary_directory_path,
                )

                try:
                    type = get_file_type_extension(
                        path=temporary_directory_path
                    )
                    return type if type is not None else str(UnknownFileType())
                except Exception:
                    return str(UnknownFileType())
