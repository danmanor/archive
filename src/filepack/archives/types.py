from tarfile import TarFile
from typing import Union
from zipfile import ZipFile

from py7zr import SevenZipFile

ArchiveObjectTypes = Union[TarFile, SevenZipFile, ZipFile]
