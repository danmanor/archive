class FileAlreadyCompressed(Exception):
    pass


class FileNotCompressed(Exception):
    pass


class FailedToGetUncompressedSize(Exception):
    pass


class FailedToGetCompressedSize(Exception):
    pass


class FailedToDecompressFile(Exception):
    pass


class FailedToCompressFile(Exception):
    pass


class CompressionTypeNotSupported(Exception):
    pass
