import pytest
from filepack.compressions.exceptions import FileAlreadyCompressed, FileNotCompressed
from filepack.compressions.lz4 import LZ4Compression
from pathlib import Path
import lz4.frame

@pytest.fixture
def uncompressed_file(tmp_path: Path):
    test_file = tmp_path / "test_file.txt"
    with test_file.open("w") as file:
        file.write("Hello, World!")
    return test_file

@pytest.fixture
def compressed_file(tmp_path: Path, uncompressed_file: Path):
    lz4_file = tmp_path / "test_file.txt.lz4"
    with lz4.frame.open(lz4_file, "wb") as file:
        file.write(uncompressed_file.read_bytes())
    return lz4_file

def test_is_compressed_should_be_false(uncompressed_file: Path):
    non_lz4_file = LZ4Compression(uncompressed_file)
    assert not non_lz4_file.is_compressed()

def test_is_compressed_should_be_true(compressed_file: Path):
    lz4_file = LZ4Compression(compressed_file)
    assert lz4_file.is_compressed()

def test_compress_raises_error_for_compressed_files(compressed_file: Path):
    lz4_file = LZ4Compression(compressed_file)
    with pytest.raises(FileAlreadyCompressed):
        lz4_file.compress()

def test_compress_file_should_be_successful(uncompressed_file: Path, tmp_path: Path):
    target_file = tmp_path / "target.lz4"
    non_lz4_file = LZ4Compression(uncompressed_file)
    non_lz4_file.compress(target_path=target_file)
    
    assert target_file.exists()
    assert LZ4Compression(target_file).is_compressed()

def test_decompress_raises_error_for_uncompressed_files(uncompressed_file: Path):
    comp = LZ4Compression(uncompressed_file)
    with pytest.raises(FileNotCompressed):
        comp.decompress(target_path="some_path.txt")

def test_decompress_file(compressed_file: Path, uncompressed_file: Path, tmp_path: Path):
    target_file = tmp_path / "decompressed.txt"
    comp = LZ4Compression(compressed_file)
    comp.decompress(target_path=target_file)

    assert target_file.read_text() == uncompressed_file.read_text()
