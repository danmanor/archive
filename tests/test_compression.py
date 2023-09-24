from pathlib import Path

from filepack.compression import Compression
from filepack.compressions.models import CompressionType


COMPRESSIONS_PATH = Path(__file__).parent / "compressions" / "compression_examples"

def test_gzip_compression_in_place(txt_file: Path, tmp_path: Path):
    comp = Compression(txt_file)
    target_path = tmp_path / f"{txt_file.name}.{CompressionType.GZIP.value}"

    uncompressed_size_before = txt_file.stat().st_size
    comp.compress(in_place=True, compression_algorithm="gz", target_path=target_path)  
    assert comp.is_compressed(compression_algorithm="gz")

    compressed_size = target_path.stat().st_size
    assert abs(comp.uncompressed_size(compression_algorithm="gz") - uncompressed_size_before) < 10
    assert abs(comp.compressed_size(compression_algorithm="gz") - compressed_size) < 10

    comp.decompress(in_place=True, compression_algorithm="gz", target_path=txt_file)
    assert comp.path.read_text() == "Hello World !"
    assert abs(comp.uncompressed_size(compression_algorithm="gz") - uncompressed_size_before) < 10
    assert abs(comp.compressed_size(compression_algorithm="gz", compression_level = 9) < compressed_size) < 10


def test_bz2_compression_in_place(txt_file: Path, tmp_path: Path):
    comp = Compression(txt_file)
    target_path = tmp_path / f"{txt_file.name}.{CompressionType.BZ2.value}"

    uncompressed_size_before = txt_file.stat().st_size
    comp.compress(compression_algorithm="bz2", target_path=target_path, in_place=True)  
    assert comp.is_compressed(compression_algorithm="bz2")

    compressed_size = target_path.stat().st_size
    assert comp.uncompressed_size(compression_algorithm="bz2") == uncompressed_size_before
    assert comp.compressed_size(compression_algorithm="bz2") == compressed_size

    comp.decompress(compression_algorithm="bz2", in_place=True, target_path=txt_file)
    assert comp.path.read_text() == "Hello World !"
    assert comp.uncompressed_size(compression_algorithm="bz2") == uncompressed_size_before
    assert comp.compressed_size(compression_algorithm="bz2", compression_level=9) == compressed_size


def test_lz4_compression_in_place(txt_file: Path, tmp_path: Path):
    comp = Compression(txt_file)
    target_path = tmp_path / f"{txt_file.name}.{CompressionType.LZ4.value}"

    uncompressed_size_before = txt_file.stat().st_size
    comp.compress(compression_algorithm="lz4", target_path=target_path, in_place=True)  
    assert comp.is_compressed(compression_algorithm="lz4")

    compressed_size = target_path.stat().st_size
    assert comp.uncompressed_size(compression_algorithm="lz4") == uncompressed_size_before
    assert comp.compressed_size(compression_algorithm="lz4") == compressed_size

    comp.decompress(compression_algorithm="lz4", target_path=txt_file, in_place=True)
    assert comp.path.read_text() == "Hello World !"
    assert comp.uncompressed_size(compression_algorithm="lz4") == uncompressed_size_before
    assert comp.compressed_size(compression_algorithm="lz4", compression_level=9) == compressed_size


def test_xz_compression_in_place(txt_file: Path, tmp_path: Path):
    comp = Compression(txt_file)
    target_path = tmp_path / f"{txt_file.name}.{CompressionType.LZ4.value}"

    uncompressed_size_before = txt_file.stat().st_size
    comp.compress(compression_algorithm="xz", target_path=target_path, in_place=True)  
    assert comp.is_compressed(compression_algorithm="xz")

    compressed_size = target_path.stat().st_size
    assert comp.uncompressed_size(compression_algorithm="xz") == uncompressed_size_before
    assert comp.compressed_size(compression_algorithm="xz") == compressed_size

    comp.decompress(compression_algorithm="xz", target_path=txt_file, in_place=True)
    assert comp.path.read_text() == "Hello World !"
    assert comp.uncompressed_size(compression_algorithm="xz") == uncompressed_size_before
    assert comp.compressed_size(compression_algorithm="xz", compression_level=9) == compressed_size


def test_gzip_compression_not_in_place(tmp_path: Path, txt_file: Path):
    comp = Compression(txt_file)
    compressed_path = tmp_path / "compressed.gz"
    decompressed_path = tmp_path / "decompressed.txt"

    comp.compress(target_path=compressed_path, compression_algorithm="gz")
    assert compressed_path.exists()

    comp_decompressed = Compression(compressed_path)
    comp_decompressed.decompress(target_path=decompressed_path, compression_algorithm="gz")

    assert decompressed_path.read_text() == "Hello World !"


def test_bz2_compression_not_in_place(tmp_path: Path, txt_file: Path):
    comp = Compression(txt_file)
    compressed_path = tmp_path / "compressed.bz2"
    decompressed_path = tmp_path / "decompressed.txt"

    comp.compress(target_path=compressed_path, compression_algorithm="bz2")
    assert compressed_path.exists()

    comp_decompressed = Compression(compressed_path)
    comp_decompressed.decompress(target_path=decompressed_path, compression_algorithm="bz2")

    assert decompressed_path.read_text() == "Hello World !"


def test_lz4_compression_not_in_place(tmp_path: Path, txt_file: Path):
    comp = Compression(txt_file)
    compressed_path = tmp_path / "compressed.lz4"
    decompressed_path = tmp_path / "decompressed.txt"

    comp.compress(target_path=compressed_path, compression_algorithm="lz4")
    assert compressed_path.exists()

    comp_decompressed = Compression(compressed_path)
    comp_decompressed.decompress(target_path=decompressed_path, compression_algorithm="lz4")

    assert decompressed_path.read_text() == "Hello World !"


def test_xz_compression_not_in_place(tmp_path: Path, txt_file: Path):
    comp = Compression(txt_file)
    compressed_path = tmp_path / "compressed.xz"
    decompressed_path = tmp_path / "decompressed.txt"

    comp.compress(target_path=compressed_path, compression_algorithm="xz")
    assert compressed_path.exists()

    comp_decompressed = Compression(compressed_path)
    comp_decompressed.decompress(target_path=decompressed_path, compression_algorithm="xz")

    assert decompressed_path.read_text() == "Hello World !"


def test_gzip_decompression_from_examples(tmp_path: Path):
    compressed_file = COMPRESSIONS_PATH / "compression_gzip.txt.gz"
    comp = Compression(compressed_file)

    assert comp.is_compressed(compression_algorithm="gz")
    decompressed_path = tmp_path / "decompressed_gzip.txt"
    comp.decompress(target_path=decompressed_path, compression_algorithm="gz")


def test_bz2_decompression_from_examples(tmp_path: Path):
    compressed_file = COMPRESSIONS_PATH / "compression_bzip2.txt.bz2"
    comp = Compression(compressed_file)

    assert comp.is_compressed(compression_algorithm="bz2")
    decompressed_path = tmp_path / "decompressed_bz2.txt"
    comp.decompress(target_path=decompressed_path, compression_algorithm="bz2")


def test_lz4_decompression_from_examples(tmp_path: Path):
    compressed_file = COMPRESSIONS_PATH / "compression_lz4.txt.lz4"
    comp = Compression(compressed_file)

    assert comp.is_compressed(compression_algorithm="lz4")
    decompressed_path = tmp_path / "decompressed_lz4.txt"
    comp.decompress(target_path=decompressed_path, compression_algorithm="lz4")


def test_xz_decompression_from_examples(tmp_path: Path):
    compressed_file = COMPRESSIONS_PATH / "compression_xz.txt.xz"
    comp = Compression(compressed_file)

    assert comp.is_compressed(compression_algorithm="xz")
    decompressed_path = tmp_path / "decompressed_xz.txt"
    comp.decompress(target_path=decompressed_path, compression_algorithm="xz")
