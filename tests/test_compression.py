from pathlib import Path

import pytest
from conftest import COMPRESSION_EXTENSIONS

from filepack.compression import Compression
from filepack.compressions.exceptions import (
    FailedToCompressFile,
    FailedToDecompressFile,
)


@pytest.mark.parametrize("compression_algorithm", COMPRESSION_EXTENSIONS)
def test_is_compressed_should_be_false(
    compression_algorithm: str, txt_file: Path
):
    compression_object = Compression(path=txt_file)
    assert not compression_object.is_compressed(
        compression_algorithm=compression_algorithm
    )


def test_is_compressed_should_be_true(compressed_file: Path):
    compressed_file, compression_algorithm = compressed_file
    compression_object = Compression(path=compressed_file)
    assert compression_object.is_compressed(
        compression_algorithm=compression_algorithm
    )


def test_compress_raises_error_for_compressed_files(compressed_file: Path):
    compressed_file, compression_algorithm = compressed_file
    compression_object = Compression(path=compressed_file)
    with pytest.raises(FailedToCompressFile):
        compression_object.compress(
            compression_algorithm=compression_algorithm
        )


@pytest.mark.parametrize("compression_algorithm", COMPRESSION_EXTENSIONS)
def test_compress_file_should_be_successful(
    compression_algorithm: str, txt_file: Path, tmp_path: Path
):
    target_file = tmp_path / "target"
    compression_object = Compression(path=txt_file)
    compression_object.compress(
        target_path=target_file, compression_algorithm=compression_algorithm
    )

    assert target_file.exists()
    compression_object = Compression(path=target_file)

    assert compression_object.is_compressed(
        compression_algorithm=compression_algorithm
    )
    target_file = tmp_path / "uncompressed"
    compression_object.decompress(
        target_path=target_file,
        compression_algorithm=compression_algorithm,
    )

    assert target_file.exists()
    assert target_file.read_bytes() == txt_file.read_bytes()


@pytest.mark.parametrize("compression_algorithm", COMPRESSION_EXTENSIONS)
def test_compress_file_in_place_should_be_successful(
    compression_algorithm: str, txt_file: Path, tmp_path: Path
):
    target_file = tmp_path / "target"
    compression_object = Compression(path=txt_file)
    compression_object.compress(
        target_path=target_file,
        compression_algorithm=compression_algorithm,
        in_place=True,
    )

    assert target_file.exists()
    assert Compression(path=target_file).is_compressed(
        compression_algorithm=compression_algorithm
    )
    assert not txt_file.exists()


@pytest.mark.parametrize("compression_algorithm", COMPRESSION_EXTENSIONS)
def test_decompress_raises_error_for_non_compressed_files(
    compression_algorithm: str, txt_file: Path
):
    compression_object = Compression(path=txt_file)
    with pytest.raises(FailedToDecompressFile):
        compression_object.decompress(
            target_path="some_path.txt",
            compression_algorithm=compression_algorithm,
        )


@pytest.mark.parametrize("compression_algorithm", COMPRESSION_EXTENSIONS)
def test_decompress_raises_error_for_compressed_files_with_different_algorithm(
    compression_algorithm: str, compressed_file: Path, txt_file: Path
):
    compressed_file, compressed_file_algorithm = compressed_file
    compression_object = Compression(path=txt_file)
    if compression_algorithm == compressed_file_algorithm:
        return

    with pytest.raises(FailedToDecompressFile):
        compression_object.decompress(
            target_path="some_path.txt",
            compression_algorithm=compression_algorithm,
        )


def test_decompress_file_should_be_successful(
    compressed_file: Path, txt_file: Path, tmp_path: Path
):
    compressed_file, compressed_file_algorithm = compressed_file
    target_file = tmp_path / "decompressed.txt"
    compression_object = Compression(path=compressed_file)
    compression_object.decompress(
        target_path=target_file,
        compression_algorithm=compressed_file_algorithm,
    )
    assert target_file.read_bytes() == txt_file.read_bytes()


def test_decompress_file_in_place_should_be_successful(
    compressed_file: Path, txt_file: Path, tmp_path: Path
):
    compressed_file, compressed_file_algorithm = compressed_file
    target_file = tmp_path / "decompressed.txt"
    compression_object = Compression(path=compressed_file)
    compression_object.decompress(
        target_path=target_file,
        compression_algorithm=compressed_file_algorithm,
        in_place=True,
    )
    assert target_file.read_bytes() == txt_file.read_bytes()
    assert not compressed_file.exists()
