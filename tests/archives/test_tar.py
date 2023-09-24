import pytest
from tarfile import TarFile, TarInfo
from pathlib import Path
from io import BytesIO

from filepack.archives.tar import TarArchive
from filepack.archives.exceptions import (
    ArchiveMemberDoesNotExist
)

@pytest.fixture
def tar_file(tmp_path: Path):
    tar_path = tmp_path / "test.tar"
    with TarFile.open(tar_path, 'w') as tar:
        content_bytes = b"Hello, World!"
        tarinfo = TarInfo(name="member.txt")
        tarinfo.size = len(content_bytes)
        tarinfo.mode = 0o644
        tar.addfile(tarinfo, BytesIO(content_bytes))

    return tar_path


def test_extract_member(tar_file: Path, tmp_path: Path):
    tar_archive = TarArchive(
        path=tar_file,
    )

    extract_to = Path(tmp_path / "extract")
    tar_archive.extract_member(
        member_name="member.txt",
        target_path=extract_to
    )

    assert (extract_to / "member.txt").read_text() == "Hello, World!"


def test_extract_non_existent_member(tar_file: Path, tmp_path: Path):
    tar_archive = TarArchive(path=tar_file)
    
    with pytest.raises(ArchiveMemberDoesNotExist):
        tar_archive.extract_member("nonexistent.txt", tmp_path)


def test_get_members_functional(tar_file: Path):
    tar_archive = TarArchive(
        path=tar_file
    )

    members = tar_archive.get_members()

    assert len(members) == 1
    assert members[0].name == "member.txt"


def test_add_member(tar_file: Path, tmp_path: Path):
    tar_archive = TarArchive(
        path=tar_file,
    )

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")
    tar_archive.add_member(
        member_path=new_file,
    )

    assert "member.txt" in [member.name for member in tar_archive.get_members()]


def test_add_non_existent_member(tar_file: Path, tmp_path: Path):
    tar_archive = TarArchive(path=tar_file)

    non_existent_file = tmp_path / "nonexistentfile.txt"

    with pytest.raises(FileNotFoundError):
        tar_archive.add_member(member_path=non_existent_file)


def test_remove_member(tar_file: Path, tmp_path: Path):
    tar_archive = TarArchive(
        path=tar_file
    )

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")

    tar_archive.add_member(
        member_path=new_file,
    )

    tar_archive.remove_member("member.txt")

    assert "member.txt" not in [member.name for member in tar_archive.get_members()]
    assert "newfile.txt" in [member.name for member in tar_archive.get_members()]


def test_remove_non_existent_member(tar_file: Path):
    tar_archive = TarArchive(path=tar_file)

    with pytest.raises(ArchiveMemberDoesNotExist):
        tar_archive.remove_member("nonexistent.txt")

