import pytest
import py7zr
from pathlib import Path
from filepack.archives.exceptions import (
    ArchiveMemberDoesNotExist
)
from filepack.archives.seven_zip import SevenZipArchive


@pytest.fixture
def seven_zip_file(tmp_path: Path):
    seven_zip_path = tmp_path / "test.7z"
    with py7zr.SevenZipFile(seven_zip_path, mode='w') as seven_zip:
        content_bytes = b"Hello, World!"
        seven_zip.writestr(data=content_bytes, arcname="member.txt")

    return seven_zip_path


def test_extract_member(seven_zip_file: Path, tmp_path: Path):
    archive = SevenZipArchive(path=seven_zip_file)
    extract_to = tmp_path / "extract"
    archive.extract_member(member_name="member.txt", target_path=extract_to)

    assert (extract_to / "member.txt").read_bytes() == b"Hello, World!"


def test_extract_non_existent_member(seven_zip_file: Path, tmp_path: Path):
    archive = SevenZipArchive(path=seven_zip_file)
    
    with pytest.raises(ArchiveMemberDoesNotExist):
        archive.extract_member("nonexistent.txt", tmp_path)


def test_get_members(seven_zip_file: Path):
    archive = SevenZipArchive(path=seven_zip_file)
    members = archive.get_members()

    assert len(members) == 1
    assert members[0].name == "member.txt"


def test_add_member(seven_zip_file: Path, tmp_path: Path):
    archive = SevenZipArchive(path=seven_zip_file)

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")
    
    archive.add_member(member_path=new_file)

    member_names = [member.name for member in archive.get_members()]
    assert "member.txt" in member_names
    assert "newfile.txt" in member_names


def test_add_non_existent_member(seven_zip_file: Path, tmp_path: Path):
    archive = SevenZipArchive(path=seven_zip_file)

    non_existent_file = tmp_path / "nonexistentfile.txt"
    
    with pytest.raises(FileNotFoundError):
        archive.add_member(member_path=non_existent_file)


def test_remove_member(seven_zip_file: Path, tmp_path: Path):
    archive = SevenZipArchive(path=seven_zip_file)

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")
    
    archive.add_member(member_path=new_file)
    archive.remove_member("member.txt")

    member_names = [member.name for member in archive.get_members()]
    assert "member.txt" not in member_names
    assert "newfile.txt" in member_names


def test_remove_non_existent_member(seven_zip_file: Path):
    archive = SevenZipArchive(path=seven_zip_file)

    with pytest.raises(ArchiveMemberDoesNotExist):
        archive.remove_member("nonexistent.txt")
