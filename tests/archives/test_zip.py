import pytest
import zipfile
from filepack.archives.zip import ZipArchive
from filepack.archives.exceptions import (
    ArchiveMemberDoesNotExist
)
from pathlib import Path

@pytest.fixture
def zip_file(tmp_path: Path):
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        content_bytes = b"Hello, World!"
        zip_file.writestr("member.txt", content_bytes)

    return zip_path


def test_extract_member(zip_file: Path, tmp_path: Path):
    zip_archive = ZipArchive(path=zip_file)
    extract_to = tmp_path / "extract"

    zip_archive.extract_member(
        member_name="member.txt",
        target_path=extract_to
    )
    
    assert (extract_to / "member.txt").read_text() == "Hello, World!"


def test_extract_non_existent_member(zip_file: Path, tmp_path: Path):
    zip_archive = ZipArchive(path=zip_file)
    
    with pytest.raises(ArchiveMemberDoesNotExist):
        zip_archive.extract_member("nonexistent.txt", tmp_path)


def test_get_members(zip_file: Path):
    zip_archive = ZipArchive(path=zip_file)

    members = zip_archive.get_members()

    assert len(members) == 1
    assert members[0].name == "member.txt"


def test_add_member(zip_file: Path, tmp_path: Path):
    zip_archive = ZipArchive(path=zip_file)
    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")

    zip_archive.add_member(new_file)

    assert "newfile.txt" in [member.name for member in zip_archive.get_members()]


def test_add_non_existent_member(zip_file: Path, tmp_path: Path):
    tar_archive = ZipArchive(path=zip_file)

    non_existent_file = tmp_path / "nonexistentfile.txt"

    with pytest.raises(FileNotFoundError):
        tar_archive.add_member(member_path=non_existent_file)


def test_remove_member(zip_file: Path, tmp_path: Path):
    zip_archive = ZipArchive(
        path=zip_file
    )

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")

    zip_archive.add_member(
        member_path=new_file,
    )

    zip_archive.remove_member(member_name="member.txt")

    assert "member.txt" not in [member.name for member in zip_archive.get_members()]
    assert "newfile.txt" in [member.name for member in zip_archive.get_members()]


def test_remove_non_existent_member(zip_file: Path):
    tar_archive = ZipArchive(path=zip_file)

    with pytest.raises(ArchiveMemberDoesNotExist):
        tar_archive.remove_member("nonexistent.txt")

