from pathlib import Path
import pytest

from filepack.archive import Archive
from filepack.archives.exceptions import (
    FailedToAddNewMemberToArchive,
    FailedToGetArchiveMembers
)


ARCHIVES_PATH = Path(__file__).parent / "archives" / "archive_examples"

def test_tar_archive(tmp_path: Path, txt_file: Path):
    new_tar_path = tmp_path / "new_tar.tar"

    arc = Archive(new_tar_path)
    arc.add_member(txt_file)

    assert len(arc.get_members()) == 1
    assert arc.get_member("new_file.txt") is not None

    extraction_path = tmp_path / "extracted"
    arc.extract_all(extraction_path)
    assert (extraction_path / "new_file.txt").read_text() == "Hello World !"

    arc.remove_member(member_name="new_file.txt")
    assert arc.get_member(member_name="new_file.txt") is None

    arc = Archive(ARCHIVES_PATH / "archive.tar")
    assert [member.name for member in arc.get_members()] == ["a.txt", "b.txt"]



def test_zip_archive(tmp_path, txt_file):
    new_tar_path = tmp_path / "new_tar.tar"

    arc = Archive(new_tar_path)
    arc.add_member(txt_file)

    assert len(arc.get_members()) == 1
    assert arc.get_member("new_file.txt") is not None

    extraction_path = tmp_path / "extracted"
    arc.extract_all(extraction_path)
    assert (extraction_path / "new_file.txt").read_text() == "Hello World !"

    arc.remove_member(member_name="new_file.txt")
    assert arc.get_member(member_name="new_file.txt") is None

    arc = Archive(ARCHIVES_PATH / "archive.zip")
    assert [member.name for member in arc.get_members()] == ["a.txt", "b.txt"]


def test_7zip_archive(tmp_path, txt_file):
    new_tar_path = tmp_path / "new_tar.tar"

    arc = Archive(new_tar_path)
    arc.add_member(txt_file)

    assert len(arc.get_members()) == 1
    assert arc.get_member("new_file.txt") is not None

    extraction_path = tmp_path / "extracted"
    arc.extract_all(extraction_path)
    assert (extraction_path / "new_file.txt").read_text() == "Hello World !"

    arc.remove_member(member_name="new_file.txt")
    assert arc.get_member(member_name="new_file.txt") is None

    arc = Archive(ARCHIVES_PATH / "archive.7z")
    assert [member.name for member in arc.get_members()] == ["a.txt", "b.txt"]


def test_rar_archive(tmp_path, txt_file):
    new_rar_path = tmp_path / "new_rar.rar"

    arc = Archive(new_rar_path)

    with pytest.raises(FailedToAddNewMemberToArchive):
        arc.add_member(txt_file)

    with pytest.raises(FailedToGetArchiveMembers):  # archive does not exist
        arc.get_members()

    arc = Archive(ARCHIVES_PATH / "archive.rar")

    assert len(arc.get_members()) == 1
    assert arc.get_member("sample-1_1.webp") is not None

    extracted_path = tmp_path / "extracted_files"
    extracted_path.mkdir(exist_ok=True)

    arc.extract_member("sample-1_1.webp", extracted_path)
    extracted_file_path = extracted_path / "sample-1_1.webp"
    assert extracted_file_path.exists()

    with pytest.raises(FailedToAddNewMemberToArchive):
        arc.add_member(txt_file)
