from pathlib import Path

import pytest
from conftest import ARCHIVE_EXTENSIONS, COMPRESSION_EXTENSIONS

from filepack.filepack import FilePack


def test_initialize_with_compressed_file_path_should_be_successful(
    compressed_file: Path,
):
    compressed_file, _ = compressed_file
    FilePack(path=compressed_file)


def test_initialize_with_uncompressed_file_path_should_be_successful(
    txt_file: Path,
):
    FilePack(path=txt_file)


def test_initialize_with_archive_file_path_should_be_successful(
    archive_file: Path,
):
    FilePack(path=archive_file)


@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_initialize_with_non_existent_archive_file_path_with_correct_suffix_should_be_successful(
    archive_extension: str,
):
    FilePack(path=Path(f"non-existent-archive.{archive_extension}"))


def test_initialize_with_non_existent_archive_file_path_with_incorrect_suffix_should_raise_an_exception():
    with pytest.raises(ExceptionGroup):
        FilePack(path="non-existent-archive.foo-bar")


@pytest.mark.parametrize("compression_algorithm", COMPRESSION_EXTENSIONS)
@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_archive_then_compress_should_be_successful(
    compression_algorithm: str,
    archive_extension: str,
    txt_file: Path,
    tmp_path: Path,
):
    new_archive_path = tmp_path / f"new_archive.{archive_extension}"

    fp = FilePack(path=new_archive_path)
    fp.add_member(member_path=txt_file)

    assert fp.get_member(member_name=txt_file.name) is not None

    compressed_archive_path = (
        new_archive_path.parent
        / f"{new_archive_path.name}.{compression_algorithm}"
    )
    fp.compress(
        target_path=compressed_archive_path,
        compression_algorithm=compression_algorithm,
        in_place=True,
    )

    assert fp.is_compressed(compression_algorithm=compression_algorithm)

    fp.decompress(
        target_path=new_archive_path,
        compression_algorithm=compression_algorithm,
        in_place=True,
    )

    assert not fp.is_compressed(compression_algorithm=compression_algorithm)

    target_file_directory_path = tmp_path / "target_dir"
    fp.extract_member(
        member_name=txt_file.name,
        target_directory_path=target_file_directory_path,
    )

    directory_files = list(target_file_directory_path.iterdir())
    assert len(directory_files) == 1
    file = directory_files[0]
    assert file.name == txt_file.name
    assert file.read_bytes() == txt_file.read_bytes()


@pytest.mark.parametrize("compression_algorithm", COMPRESSION_EXTENSIONS)
@pytest.mark.parametrize("archive_extension", ARCHIVE_EXTENSIONS)
def test_compress_then_archive_should_be_successful(
    compression_algorithm: str,
    archive_extension: str,
    txt_file: Path,
    tmp_path: Path,
):
    compressed_file_path = (
        txt_file.parent / f"{txt_file.name}.{compression_algorithm}"
    )
    fp = FilePack(path=txt_file)
    fp.compress(
        target_path=compressed_file_path,
        compression_algorithm=compression_algorithm,
    )

    fp = FilePack(path=compressed_file_path)
    assert fp.is_compressed(compression_algorithm=compression_algorithm)

    new_archive_path = tmp_path / f"new_archive.{archive_extension}"
    fp = FilePack(path=new_archive_path)
    fp.add_member(member_path=compressed_file_path)

    assert fp.get_member(member_name=compressed_file_path.name) is not None

    target_file_directory_path = tmp_path / "target_dir"
    fp.extract_member(
        member_name=compressed_file_path.name,
        target_directory_path=target_file_directory_path,
    )

    directory_files = list(target_file_directory_path.iterdir())
    assert len(directory_files) == 1
    file = directory_files[0]
    assert file.name == compressed_file_path.name

    fp = FilePack(path=file)
    uncompressed_file = tmp_path / "uncompressed.txt"

    fp.decompress(
        target_path=uncompressed_file,
        compression_algorithm=compression_algorithm,
    )

    fp = FilePack(path=uncompressed_file)
    assert not fp.is_compressed(compression_algorithm=compression_algorithm)
    assert uncompressed_file.read_bytes() == txt_file.read_bytes()
