import pytest
from filepack.compressions.exceptions import (
    FileAlreadyCompressed, 
    FileNotCompressed
)
from pathlib import Path
import gzip

from filepack.compressions.gzip import GzipCompression

@pytest.fixture
def uncompressed_file(tmp_path: Path):
    test_file = tmp_path / "test_file.txt"
    with test_file.open("w") as file:
        file.write("Hello, World!")

    return test_file


@pytest.fixture
def compressed_file(tmp_path: Path, uncompressed_file: Path):
    gzip_file = tmp_path / "test_file.txt.gz"
    with gzip.open(gzip_file, "wb") as file:
        file.write(uncompressed_file.read_bytes())

    return gzip_file


def test_is_compressed_should_be_false(uncompressed_file: Path):
    non_gzip_file = GzipCompression(uncompressed_file)
    assert not non_gzip_file.is_compressed()


def test_is_compressed_should_be_true(compressed_file: Path):
    gzip_file = GzipCompression(compressed_file)
    assert gzip_file.is_compressed()


def test_compress_raises_error_for_compressed_files(compressed_file: Path):
    gzip_file = GzipCompression(compressed_file)
    with pytest.raises(FileAlreadyCompressed):
        gzip_file.compress()


def test_compress_file_should_be_successfull(uncompressed_file: Path, tmp_path: Path):
    target_file = tmp_path / "target.gz"
    non_gzip_file = GzipCompression(uncompressed_file)
    non_gzip_file.compress(target_file)

    assert target_file.exists()
    assert GzipCompression(target_file).is_compressed()


def test_decompress_raises_error_for_uncompressed_files(uncompressed_file: Path):
    comp = GzipCompression(uncompressed_file)
    with pytest.raises(FileNotCompressed):
        comp.decompress("some_path.txt")


def test_decompress_file(compressed_file: Path, uncompressed_file: Path, tmp_path: Path):
    target_file = tmp_path / "decompressed.txt"
    comp = GzipCompression(compressed_file)
    comp.decompress(target_file)

    assert target_file.read_bytes() == uncompressed_file.read_bytes()
