from pathlib import Path

import pytest
from conftest import ARCHIVE_EXTENSIONS, ARCHIVE_MEMBER_NAME

from filepack.archive import Archive
from filepack.archives.exceptions import (
    FailedToAddNewMemberToArchive,
    FailedToExtractArchiveMember,
    FailedToRemoveArchiveMember,
)


def test_extract_member(archive_file: Path, tmp_path: Path):
    archive = Archive(
        path=archive_file,
    )

    extract_to = Path(tmp_path / "extract")
    archive.extract_member(
        member_name=ARCHIVE_MEMBER_NAME, target_directory_path=extract_to
    )

    assert (extract_to / ARCHIVE_MEMBER_NAME).read_text() == "Hello, World!"
    assert archive.get_member(member_name=ARCHIVE_MEMBER_NAME) is not None


def test_extract_member_in_place(archive_file: Path, tmp_path: Path):
    archive = Archive(
        path=archive_file,
    )

    extract_to = Path(tmp_path / "extract")
    archive.extract_member(
        member_name=ARCHIVE_MEMBER_NAME,
        target_directory_path=extract_to,
        in_place=True,
    )

    assert (extract_to / ARCHIVE_MEMBER_NAME).read_text() == "Hello, World!"
    assert archive.get_member(member_name=ARCHIVE_MEMBER_NAME) is None


def test_extract_non_existent_member(archive_file: Path, tmp_path: Path):
    archive = Archive(path=archive_file)

    with pytest.raises(FailedToExtractArchiveMember):
        archive.extract_member("nonexistent.txt", tmp_path)


@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_extract_non_existent_member_no_archive(
    archive_extension: str, tmp_path: Path
):
    archive = Archive(path=tmp_path / f"some_path.{archive_extension}")

    with pytest.raises(FailedToExtractArchiveMember):
        archive.extract_member("nonexistent.txt", tmp_path)


def test_extract_all(archive_file: Path, tmp_path: Path):
    archive = Archive(
        path=archive_file,
    )

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")
    archive.add_member(
        member_path=new_file,
    )

    extract_to = Path(tmp_path / "extract")
    archive.extract_all(target_directory_path=extract_to)

    assert (extract_to / ARCHIVE_MEMBER_NAME).read_text() == "Hello, World!"
    assert (extract_to / new_file.name).read_text() == "New content!"
    assert len(archive.get_members()) == 2


def test_extract_all_in_place(archive_file: Path, tmp_path: Path):
    archive = Archive(
        path=archive_file,
    )

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")
    archive.add_member(
        member_path=new_file,
    )

    extract_to = Path(tmp_path / "extract")
    archive.extract_all(target_directory_path=extract_to, in_place=True)

    assert (extract_to / ARCHIVE_MEMBER_NAME).read_text() == "Hello, World!"
    assert (extract_to / new_file.name).read_text() == "New content!"
    assert len(archive.get_members()) == 0


def test_extract_all_no_members(archive_file: Path, tmp_path: Path):
    archive = Archive(
        path=archive_file,
    )

    archive.remove_member(member_name=ARCHIVE_MEMBER_NAME)

    extract_to = Path(tmp_path / "extract")
    archive.extract_all(target_directory_path=extract_to)

    assert extract_to.exists() == False


@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_extract_all_no_members_no_archive(
    archive_extension: str, tmp_path: Path
):
    archive = Archive(path=tmp_path / f"some_path.{archive_extension}")

    extract_to = Path(tmp_path / "extract")
    archive.extract_all(target_directory_path=extract_to)

    assert extract_to.exists() == False


def test_get_members(archive_file: Path):
    archive = Archive(path=archive_file)

    members = archive.get_members()

    assert len(members) == 1
    assert members[0].name == ARCHIVE_MEMBER_NAME


def test_get_members_no_files(archive_file: Path):
    archive = Archive(path=archive_file)

    archive.remove_member(member_name=ARCHIVE_MEMBER_NAME)

    assert archive.get_members() == []


@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_get_members_no_files_no_archive(
    archive_extension: str, tmp_path: Path
):
    archive = Archive(path=tmp_path / f"some_path.{archive_extension}")

    members = archive.get_members()

    assert len(members) == 0


def test_get_member(archive_file: Path):
    archive = Archive(path=archive_file)

    member = archive.get_member(ARCHIVE_MEMBER_NAME)
    assert member is not None
    assert member.name == ARCHIVE_MEMBER_NAME


def test_get_non_existent_member(archive_file: Path):
    archive = Archive(path=archive_file)

    member = archive.get_member("nonexistent.txt")
    assert member is None


@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_get_non_existent_member_no_archive(
    archive_extension: str, tmp_path: Path
):
    archive = Archive(path=tmp_path / f"some_path.{archive_extension}")

    member = archive.get_member("nonexistent.txt")

    assert member is None


def test_add_member_archive_exists(archive_file: Path, tmp_path: Path):
    archive = Archive(
        path=archive_file,
    )

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")
    archive.add_member(
        member_path=new_file,
    )

    assert ARCHIVE_MEMBER_NAME in [
        member.name for member in archive.get_members()
    ]
    assert new_file.exists()


def test_add_member_archive_exists_in_place(
    archive_file: Path, tmp_path: Path
):
    archive = Archive(
        path=archive_file,
    )

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")
    archive.add_member(member_path=new_file, in_place=True)

    assert ARCHIVE_MEMBER_NAME in [
        member.name for member in archive.get_members()
    ]
    assert new_file.exists() == False


@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_add_member_no_archive(archive_extension: str, tmp_path: Path):
    archive = Archive(
        path=tmp_path / f"some_path.{archive_extension}",
    )

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")
    archive.add_member(
        member_path=new_file,
    )

    assert "newfile.txt" in [member.name for member in archive.get_members()]


def test_add_non_existent_member(archive_file: Path, tmp_path: Path):
    archive = Archive(path=archive_file)

    non_existent_file = tmp_path / "nonexistentfile.txt"

    with pytest.raises(FailedToAddNewMemberToArchive):
        archive.add_member(member_path=non_existent_file)


def test_remove_member(archive_file: Path, tmp_path: Path):
    archive = Archive(path=archive_file)

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")

    archive.add_member(
        member_path=new_file,
    )

    archive.remove_member(member_name=ARCHIVE_MEMBER_NAME)

    assert ARCHIVE_MEMBER_NAME not in [
        member.name for member in archive.get_members()
    ]
    assert "newfile.txt" in [member.name for member in archive.get_members()]


def test_remove_non_existent_member(archive_file: Path):
    archive = Archive(path=archive_file)

    with pytest.raises(FailedToRemoveArchiveMember):
        archive.remove_member(member_name="nonexistent.txt")


@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_remove_non_existent_member_no_archive(
    archive_extension: str, tmp_path: Path
):
    archive = Archive(path=tmp_path / f"some_path.{archive_extension}")

    with pytest.raises(FailedToRemoveArchiveMember):
        archive.remove_member(member_name="nonexistent.txt")


def test_remove_all(archive_file: Path, tmp_path: Path):
    archive = Archive(path=archive_file)

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")

    archive.add_member(
        member_path=new_file,
    )

    archive.remove_all()

    assert archive.get_members() == []


def test_remove_all_no_members(archive_file: Path):
    archive = Archive(path=archive_file)

    archive.remove_member(
        member_name=ARCHIVE_MEMBER_NAME,
    )

    archive.remove_all()

    assert archive.get_members() == []


@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_remove_all_no_members_no_archive(
    archive_extension: str, tmp_path: Path
):
    archive = Archive(path=f"some_file.{archive_extension}")

    new_file = tmp_path / "newfile.txt"
    new_file.write_text("New content!")

    archive.add_member(
        member_path=new_file,
    )

    archive.remove_all()

    assert archive.get_members() == []
