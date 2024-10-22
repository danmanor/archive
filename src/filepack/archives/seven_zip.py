from pathlib import Path
from typing import cast

from py7zr import FileInfo, SevenZipFile

from filepack.archives.models import (
    AbsractArchiveClient,
    AbstractArchiveMember,
    AbstractArchiveObject,
)
from filepack.archives.types import ArchiveObjectTypes


class SevenZipObject(AbstractArchiveObject):
    def __init__(
        self,
        archive_object: ArchiveObjectTypes,
        client: AbsractArchiveClient,
        archive_path: Path,
    ) -> None:
        super().__init__(
            archive_object=archive_object, client=client, path=archive_path
        )
        assert isinstance(self._archive_object, SevenZipFile)
        self._archive_object = cast(SevenZipFile, self._archive_object)

    def get_members(self) -> list[AbstractArchiveMember]:
        return [
            SevenZipMember(
                member=seven_zip_info_object,
                client=self._client,
                archive_path=self._path,
            )
            for seven_zip_info_object in self._archive_object.list()  # type: ignore
        ]

    def extract_member(self, member_name: str, target_directory_path: Path):
        self._archive_object.extract(  # type: ignore
            targets=[member_name], path=target_directory_path
        )

    def add_member(self, member_path: Path):
        self._archive_object.write(file=member_path, arcname=member_path.name)  # type: ignore


class SevenZipClient(AbsractArchiveClient):
    def open(self, file_path: Path, mode: str) -> AbstractArchiveObject:
        return SevenZipObject(
            archive_object=SevenZipFile(file=file_path, mode=mode),
            client=self,
            archive_path=file_path,
        )


class SevenZipMember(AbstractArchiveMember):
    def __init__(
        self,
        member: FileInfo,
        client: AbsractArchiveClient,
        archive_path: Path,
    ) -> None:
        super().__init__(
            client=client,
            archive_path=archive_path,
            name=member.filename,
            size=member.compressed,
            mtime=member.creationtime.strftime("%a, %d %b %Y %H:%M:%S UTC"),
        )
