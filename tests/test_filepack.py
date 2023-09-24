import pytest
from pathlib import Path
import filetype

import zipfile
import py7zr
import tarfile
import shutil

from filepack.filepack import FilePack
from filepack.compressions.consts import (
    SUPPORTED_COMPRESSIONS_SUFFIXES
)


ARCHIVES_PATH = Path(__file__).parent / "archives" / "archive_examples"

@pytest.fixture
def tar_file(tmp_path: Path, txt_file: Path) -> Path:
    zip_path = tmp_path / "test.rar"
    with tarfile.TarFile(zip_path, 'w') as tar_file:
        tar_file.add(txt_file, txt_file.name)
    return zip_path

@pytest.fixture
def zip_file(tmp_path: Path, txt_file: Path) -> Path:
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(txt_file, txt_file.name)
    return zip_path

@pytest.fixture
def seven_zip_file(tmp_path: Path, txt_file: Path) -> Path:
    sevenz_path = tmp_path / "test.7z"
    with py7zr.SevenZipFile(sevenz_path, 'w') as archive:
        archive.write(txt_file, txt_file.name)
    return sevenz_path

@pytest.fixture
def rar_file() -> Path:
    return ARCHIVES_PATH / "archive.rar"

@pytest.fixture
def archives(tar_file: Path, zip_file: Path, seven_zip_file: Path, rar_file: Path) -> list[Path]:
    return [tar_file, zip_file, seven_zip_file, rar_file]


def test_sizes_with_valid_instances(txt_file: Path):
    fp = FilePack(path=txt_file)

    for compression in SUPPORTED_COMPRESSIONS_SUFFIXES:
        uncompressed_size = fp.path.stat().st_size
        
        fp.compress(
            compression_algorithm=compression,
            compression_level=9,
            in_place=True
        )

        assert fp.is_compressed(compression_algorithm=compression)

        compressed_size = fp.path.stat().st_size
        fp.decompress(compression_algorithm=compression, in_place=True)

        assert not fp.is_compressed(compression_algorithm=compression)
        assert abs(uncompressed_size - fp.path.stat().st_size) < 10 
        assert abs(fp.uncompressed_size(
            compression_algorithm=compression
        ) - fp.path.stat().st_size) < 10
        assert abs(compressed_size - fp.compressed_size(
            compression_algorithm=compression,
            compression_level=9
        )) < 10


def test_sizes_with_invalid_instances(txt_file: Path):
    fp = FilePack(path=txt_file)

    with pytest.raises(Exception):
        fp.compress(
            compression_algorithm="non-existed-type"
        )


def test_add_member_with_valid_memeber(archives: list[Path], txt_file: Path):
    for archive_path in archives:
        fp = FilePack(path=archive_path)

        if filetype.guess(archive_path).extension == "rar":
            continue
        fp.add_member(member_path=txt_file)

        assert ["new_file.txt", "new_file.txt"] == fp.get_members_name()


def test_add_member_with_invalid_memeber(archives: list[Path]):
    for archive_path in archives:
        fp = FilePack(path=archive_path)
        if filetype.guess(archive_path).extension == "rar":
            continue
        with pytest.raises(Exception):
            fp.add_member(member_path="non-existent-member")


def test_remove_member_with_valid_member(archives: list[Path], txt_file: Path):
    for archive_path in archives:
        if filetype.guess(archive_path).extension == "rar":
            continue
        fp = FilePack(path=archive_path)
        member_name = txt_file.name
        fp.add_member(member_path=txt_file)
        fp.remove_member(member_name=member_name)
        assert member_name not in fp.get_members_name()


def test_add_remove_with_valid_member(archives: list[Path], txt_file: Path):
    for archive_path in archives:
        if filetype.guess(archive_path).extension == "rar":
            continue
        fp = FilePack(path=archive_path)
        member_name = txt_file.name
        fp.add_member(member_path=txt_file)
        assert member_name in fp.get_members_name()
        fp.remove_member(member_name=member_name)
        assert member_name not in fp.get_members_name()

def test_extract_member_with_valid_member(archives: list[Path], tmp_path: Path):
    for archive_path in archives:
        fp = FilePack(path=archive_path)

        target_path = tmp_path / "extracted"
        target_path.mkdir(exist_ok=True)

        if filetype.guess(archive_path).extension == "rar":
            fp.extract_member(member_name="sample-1_1.webp", target_path=target_path)
            extracted_file_path = target_path / "sample-1_1.webp"
            assert extracted_file_path.exists()
            continue

        fp.extract_member(member_name="new_file.txt", target_path=target_path)
        extracted_file_path = target_path / "new_file.txt"
        assert extracted_file_path.exists()

def test_extract_member_with_invalid_member(archives: list[Path], tmp_path: Path):
    for archive_path in archives:
        fp = FilePack(path=archive_path)
        target_path = tmp_path / "extracted"
        target_path.mkdir(exist_ok=True)
        with pytest.raises(Exception):
            fp.extract_member(member_name="non-existent-member", target_path=target_path)

def test_get_members_with_some_members(archives: list[Path], txt_file: Path):
    for archive_path in archives:
        fp = FilePack(path=archive_path)

        assert len(fp.get_members()) == 1

def test_remove_all_members_with_no_members(archives: list[Path]):
    for archive_path in archives:
        if filetype.guess(archive_path).extension == "rar":
            continue

        fp = FilePack(path=archive_path)
        fp.remove_all()

        assert len(fp.get_members()) == 0

        fp.remove_all()


def test_remove_all_members_with_some_members(archives: list[Path]):
    for archive_path in archives:
        if filetype.guess(archive_path).extension == "rar":
            continue

        fp = FilePack(path=archive_path)
        
        fp.remove_all()
        assert len(fp.get_members()) == 0

def test_get_member_with_valid_member(archives: list[Path]):
    for archive_path in archives:
        fp = FilePack(path=archive_path)
        if filetype.guess(archive_path).extension == "rar":
            member = fp.get_member("sample-1_1.webp")
            assert member is not None
            continue
    
        member = fp.get_member("new_file.txt")

        assert member is not None
        assert member.name == "new_file.txt"

def test_get_member_with_invalid_member(archives: list[Path]):
    for archive_path in archives:
        fp = FilePack(path=archive_path)
        member = fp.get_member("non-existent-member")
        assert member is None

def test_compress_archive_with_valid_archive(tmp_path: Path, archives: list[Path]):
    for archive_path in archives:
        fp = FilePack(path=archive_path)

        if filetype.guess(archive_path).extension == "rar":
            duplicate_path = tmp_path / "duplicate"
            shutil.copy(src=archive_path, dst=duplicate_path)
            fp = FilePack(path=duplicate_path)

        for compression in SUPPORTED_COMPRESSIONS_SUFFIXES:
            fp.compress(compression_algorithm=compression, in_place=True)
            assert fp.is_compressed(compression_algorithm=compression)

def test_compress_archive_with_invalid_archive(tmp_path: Path):
    invalid_archive_path = tmp_path / "test.invalid"
    invalid_archive_path.touch()
    fp = FilePack(path=invalid_archive_path)
    with pytest.raises(Exception):
        fp.compress(compression_algorithm="zip")
