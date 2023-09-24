from typing import Final

from filepack.archives.rar import RarArchive
from filepack.archives.seven_zip import SevenZipArchive
from filepack.archives.tar import TarArchive
from filepack.archives.zip import ZipArchive
from filepack.compressions.bzip2 import BzipCompression
from filepack.compressions.gzip import GzipCompression
from filepack.compressions.lz4 import LZ4Compression
from filepack.compressions.xz import XZCompression

ERROR_MESSAGE_NOT_SUPPORTED: Final[
    str
] = "the given file inferred type is not supported"

SUPPORTED_COMPRESSION_CLASSES = [
    BzipCompression,
    GzipCompression,
    LZ4Compression,
    XZCompression,
]

SUPPORTED_ARCHIVE_CLASSES = [
    ZipArchive,
    TarArchive,
    SevenZipArchive,
    RarArchive,
]
