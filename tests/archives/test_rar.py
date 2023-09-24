import pytest
from pathlib import Path

from filepack.archives.exceptions import (
    ArchiveMemberDoesNotExist,
    FailedToAddNewMemberToArchive,
    FailedToRemoveArchiveMember
)
from filepack.archives.rar import RarArchive

@pytest.fixture
def rar_file(tmp_path: Path):
    current_file_dir = Path(__file__).parent
    RAR_SAMPLE_PATH = current_file_dir / "archive_examples" / "archive.rar"
    new_rar_path = tmp_path / "test.rar"

    with open(RAR_SAMPLE_PATH, "rb") as rar_file:
        with open(new_rar_path, "wb") as new_rar_file:
            new_rar_file.write(rar_file.read())

    return new_rar_path


def test_extract_member(rar_file: Path, tmp_path: Path):
    archive = RarArchive(path=rar_file)
    extract_to = tmp_path / "extract"
    archive.extract_member(member_name="sample-1_1.webp", target_path=extract_to)

    assert (extract_to / "sample-1_1.webp").exists()


def test_extract_non_existent_member(rar_file: Path, tmp_path: Path):
    archive = RarArchive(path=rar_file)
    
    with pytest.raises(ArchiveMemberDoesNotExist):
        archive.extract_member("nonexistent.txt", tmp_path)


def test_get_members(rar_file: Path):
    archive = RarArchive(path=rar_file)
    members = archive.get_members()

    assert any(member.name == "sample-1_1.webp" for member in members)


def test_add_member(rar_file: Path, tmp_path: Path):
    archive = RarArchive(path=rar_file)
    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")
    
    with pytest.raises(FailedToAddNewMemberToArchive):
        archive.add_member(member_path=new_file)


def test_remove_member(rar_file: Path):
    archive = RarArchive(path=rar_file)

    with pytest.raises(FailedToRemoveArchiveMember):
        archive.remove_member("sample-1_1.webp")
