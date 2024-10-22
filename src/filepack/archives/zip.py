from datetime import datetime, timezone
from pathlib import Path
from typing import cast
from zipfile import ZipFile, ZipInfo

from filepack.archives.models import (
    AbsractArchiveClient,
    AbstractArchiveMember,
    AbstractArchiveObject,
)
from filepack.archives.types import ArchiveObjectTypes


class ZipObject(AbstractArchiveObject):
    def __init__(
        self,
        archive_object: ArchiveObjectTypes,
        client: AbsractArchiveClient,
        archive_path: Path,
    ) -> None:
        super().__init__(
            archive_object=archive_object, client=client, path=archive_path
        )
        assert isinstance(self._archive_object, ZipFile)
        self._archive_object = cast(ZipFile, self._archive_object)

    def get_members(self) -> list[AbstractArchiveMember]:
        return [
            ZipMember(
                member=zip_info_object,
                client=self._client,
                archive_path=self._path,
            )
            for zip_info_object in self._archive_object.infolist()  # type: ignore
        ]

    def extract_member(self, member_name: str, target_directory_path: Path):
        self._archive_object.extract(  # type: ignore
            member=member_name, path=target_directory_path
        )

    def add_member(self, member_path: Path):
        self._archive_object.write(  # type: ignore
            filename=member_path, arcname=member_path.name
        )


class ZipClient(AbsractArchiveClient):
    def open(self, file_path: Path, mode: str) -> AbstractArchiveObject:
        return ZipObject(
            archive_object=ZipFile(file=file_path, mode=mode),  # type: ignore
            client=self,
            archive_path=file_path,
        )


class ZipMember(AbstractArchiveMember):
    def __init__(
        self, member: ZipInfo, client: AbsractArchiveClient, archive_path: Path
    ) -> None:
        super().__init__(
            client=client,
            archive_path=archive_path,
            name=member.filename,
            size=member.file_size,
            mtime=datetime.fromtimestamp(
                datetime(*member.date_time).timestamp(), tz=timezone.utc
            ).strftime("%a, %d %b %Y %H:%M:%S UTC"),
        )
