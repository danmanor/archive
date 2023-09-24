import pytest
from filepack.compressions.exceptions import (
    FileAlreadyCompressed, 
    FileNotCompressed
)
from pathlib import Path
import lzma

from filepack.compressions.xz import XZCompression

@pytest.fixture
def uncompressed_file(tmp_path: Path):
    test_file = tmp_path / "test_file.txt"
    with test_file.open("w") as file:
        file.write("Hello, World!")
    return test_file


@pytest.fixture
def compressed_file(tmp_path: Path, uncompressed_file: Path):
    xz_file = tmp_path / "test_file.txt.xz"
    with lzma.open(xz_file, "wb") as file:
        file.write(uncompressed_file.read_bytes())
    return xz_file


def test_is_compressed_should_be_false(uncompressed_file: Path):
    non_xz_file = XZCompression(uncompressed_file)
    assert not non_xz_file.is_compressed()


def test_is_compressed_should_be_true(compressed_file: Path):
    xz_file = XZCompression(compressed_file)
    assert xz_file.is_compressed()


def test_compress_raises_error_for_compressed_files(compressed_file: Path):
    xz_file = XZCompression(compressed_file)
    with pytest.raises(FileAlreadyCompressed):
        xz_file.compress()


def test_compress_file_should_be_successfull(uncompressed_file: Path, tmp_path: Path):
    target_file = tmp_path / "targset.xz"
    non_xz_file = XZCompression(uncompressed_file)
    non_xz_file.compress(target_file)

    assert target_file.exists()
    assert XZCompression(target_file).is_compressed()


def test_decompress_raises_error_for_uncompressed_files(uncompressed_file: Path):
    comp = XZCompression(uncompressed_file)
    with pytest.raises(FileNotCompressed):
        comp.decompress("some_path.txt")


def test_decompress_file(compressed_file: Path, uncompressed_file: Path, tmp_path: Path):
    target_file = tmp_path / "decompressed.txt"
    comp = XZCompression(compressed_file)
    comp.decompress(target_file)

    assert target_file.read_bytes() == uncompressed_file.read_bytes()
