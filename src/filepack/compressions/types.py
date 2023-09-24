from bz2 import BZ2File
from gzip import GzipFile
from lzma import LZMAFile
from typing import Union

from lz4.frame import LZ4FrameFile

CompressionObjectTypes = Union[GzipFile, LZ4FrameFile, LZMAFile, BZ2File]
