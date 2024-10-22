import bz2
import gzip
import lzma
from io import BytesIO
from pathlib import Path
from tarfile import TarFile, TarInfo
from zipfile import ZipFile

import lz4.frame
import pytest
from py7zr import SevenZipFile

from filepack.archives.consts import SEVEN_ZIP_SUFFIX, TAR_SUFFIX, ZIP_SUFFIX
from filepack.compressions.consts import (
    BZ2_SUFFIX,
    GZIP_SUFFIX,
    LZ4_SUFFIX,
    XZ_SUFFIX,
)

ARCHIVE_MEMBER_NAME = "member.txt"
ARCHIVE_EXTENSIONS = [SEVEN_ZIP_SUFFIX, ZIP_SUFFIX, TAR_SUFFIX]
ARCHIVE_METHODS = {
    SEVEN_ZIP_SUFFIX: lambda path: create_seven_zip(path),
    TAR_SUFFIX: lambda path: create_tar_archive(path),
    ZIP_SUFFIX: lambda path: create_zip_archive(path),
}
COMPRESSION_EXTENSIONS = [XZ_SUFFIX, GZIP_SUFFIX, LZ4_SUFFIX, BZ2_SUFFIX]
COMPRESSION_METHODS = {
    BZ2_SUFFIX: lambda f: bz2.open(f, "wb"),
    GZIP_SUFFIX: lambda f: gzip.open(f, "wb"),
    XZ_SUFFIX: lambda f: lzma.open(f, "wb"),
    LZ4_SUFFIX: lambda f: lz4.frame.open(f, "wb"),
}


def create_seven_zip(seven_zip_path: Path):
    with SevenZipFile(seven_zip_path, mode="w") as seven_zip:
        content_bytes = b"Hello, World!"
        seven_zip.writestr(data=content_bytes, arcname=ARCHIVE_MEMBER_NAME)
    return seven_zip_path


def create_tar_archive(tar_path: Path):
    with TarFile.open(tar_path, "w") as tar:
        content_bytes = b"Hello, World!"
        tarinfo = TarInfo(name=ARCHIVE_MEMBER_NAME)
        tarinfo.size = len(content_bytes)
        tarinfo.mode = 0o644
        tar.addfile(tarinfo, BytesIO(content_bytes))
    return tar_path


def create_zip_archive(zip_path: Path):
    with ZipFile(zip_path, "w") as zip_file:
        content_bytes = b"Hello, World!"
        zip_file.writestr(ARCHIVE_MEMBER_NAME, content_bytes)
    return zip_path


@pytest.fixture
def txt_file(tmp_path: Path) -> Path:
    txt_file_path = tmp_path / "new_file.txt"
    with open(txt_file_path, "w") as file:
        file.write("Hello World !")

    return txt_file_path


@pytest.fixture(params=ARCHIVE_EXTENSIONS)
def archive_file(request: pytest.FixtureRequest, tmp_path: Path):
    extension = request.param
    archive_path = tmp_path / f"test.{extension}"
    archive_func = ARCHIVE_METHODS.get(extension)

    if archive_func is None:
        raise ValueError(f"Unsupported archive extension {extension}")

    return archive_func(archive_path)


@pytest.fixture(params=COMPRESSION_EXTENSIONS)
def compressed_file(
    request: pytest.FixtureRequest, tmp_path: Path, txt_file: Path
):
    extension = request.param
    compressed_file_path = tmp_path / f"test_file.txt{extension}"
    compression_func = COMPRESSION_METHODS.get(extension)

    if compression_func is None:
        raise ValueError(f"Unsupported compression extension {extension}")

    with compression_func(compressed_file_path) as file:
        file.write(txt_file.read_bytes())

    return compressed_file_path, extension
