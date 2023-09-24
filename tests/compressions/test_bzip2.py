import pytest
from filepack.compressions.exceptions import (
    FileAlreadyCompressed, 
    FileNotCompressed
)
from pathlib import Path
import bz2

from filepack.compressions.bzip2 import BzipCompression

@pytest.fixture
def uncompressed_file(tmp_path: Path):
    test_file = tmp_path / "test_file.txt"
    with test_file.open("w") as file:
        file.write("Hello, World!")

    return test_file


@pytest.fixture
def compressed_file(tmp_path: Path, uncompressed_file: Path):
    bz2_file = tmp_path / "test_file.txt.bz2"
    with bz2.open(bz2_file, "wb") as file:
        file.write(uncompressed_file.read_bytes())

    return bz2_file


def test_is_compressed_should_be_false(uncompressed_file: Path):
    non_bz2_file = BzipCompression(uncompressed_file)
    assert not non_bz2_file.is_compressed()


def test_is_compressed_should_be_true(compressed_file: Path):
    bz2_file = BzipCompression(compressed_file)
    assert bz2_file.is_compressed()


def test_compress_raises_error_for_compressed_files(compressed_file: Path):
    bz2_file = BzipCompression(compressed_file)
    with pytest.raises(FileAlreadyCompressed):
        bz2_file.compress()


def test_compress_file_should_be_successfull(compressed_file: Path, uncompressed_file: Path, tmp_path: Path):
    target_file = tmp_path / "target.bz2"
    non_bz2_file = BzipCompression(uncompressed_file)
    non_bz2_file.compress(target_file)

    assert target_file.exists()
    assert BzipCompression(target_file).is_compressed()


def test_decompress_raises_error_for_uncompressed_files(uncompressed_file: Path):
    comp = BzipCompression(uncompressed_file)
    with pytest.raises(FileNotCompressed):
        comp.decompress("some_path.txt")


def test_decompress_file(compressed_file: Path, uncompressed_file: Path, tmp_path: Path):
    target_file = tmp_path / "decompressed.txt"
    comp = BzipCompression(compressed_file)
    comp.decompress(target_file)

    assert target_file.read_bytes() == uncompressed_file.read_bytes()
