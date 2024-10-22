from datetime import datetime, timezone
from pathlib import Path
from tarfile import TarFile, TarInfo
from typing import Literal, cast

from filepack.archives.models import (
    AbsractArchiveClient,
    AbstractArchiveMember,
    AbstractArchiveObject,
)
from filepack.archives.types import ArchiveObjectTypes


class TarObject(AbstractArchiveObject):
    def __init__(
        self,
        archive_object: ArchiveObjectTypes,
        client: AbsractArchiveClient,
        archive_path: Path,
    ) -> None:
        super().__init__(
            archive_object=archive_object, client=client, path=archive_path
        )
        assert isinstance(self._archive_object, TarFile)
        self._archive_object = cast(TarFile, self._archive_object)

    def get_members(self) -> list[AbstractArchiveMember]:
        return [
            TarMember(
                member=tar_info_object,
                client=self._client,
                archive_path=self._path,
            )
            for tar_info_object in self._archive_object.getmembers()  # type: ignore
        ]

    def extract_member(self, member_name: str, target_directory_path: Path):
        self._archive_object.extract(  # type: ignore
            member=member_name, path=target_directory_path
        )

    def add_member(self, member_path: Path):
        self._archive_object.add(name=member_path, arcname=member_path.name)  # type: ignore


class TarClient(AbsractArchiveClient):
    def open(self, file_path: Path, mode: str) -> AbstractArchiveObject:
        if mode not in ["r", "a", "w", "x"]:
            raise ValueError("mode must be one of ['r', 'a', 'w', 'x']")

        mode = cast(Literal["r", "a", "w", "x"], mode)
        return TarObject(
            archive_object=TarFile(name=file_path, mode=mode),
            client=self,
            archive_path=file_path,
        )


class TarMember(AbstractArchiveMember):
    def __init__(
        self, member: TarInfo, client: AbsractArchiveClient, archive_path: Path
    ) -> None:
        super().__init__(
            client=client,
            archive_path=archive_path,
            name=member.name,
            size=member.size,
            mtime=datetime.fromtimestamp(
                member.mtime, tz=timezone.utc
            ).strftime("%a, %d %b %Y %H:%M:%S UTC"),
        )
