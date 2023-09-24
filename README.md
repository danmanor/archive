# filepack

A user-friendly interface for handling files, archives, and compressed files in Python.

## Features

- Unified interface for working with both archives and compressed files.
- Support for various archive formats: `TAR`, `ZIP`, `SEVEN_ZIP`.
- Support for popular compression algorithms: `GZIP`, `BZ2`, `LZ4`, `XZ`.
- Streamlined methods for file compression, decompression, archive extraction, and more.

## Installation
```bash
pip install filepack
```

## API Overview

### FilePack

The `FilePack` class is the main interface, combining both archive and compression operations. It automatically identifies whether the input is an archive or a compressed file and provides methods for handling both.

| Method/Property       | Description                                                 |
|-----------------------|-------------------------------------------------------------|
| `path`                | Returns the path of the file or archive.                    |
| `size`                | Returns the size of the file or archive in bytes.           |
| `is_compressed`       | Check if the file is compressed using a specified algorithm.|
| `uncompressed_size`   | Get uncompressed size for compressed files.                 |
| `compressed_size`     | Get compressed size for files.                              |
| `compression_ratio`   | Get compression ratio for compressed files.                 |
| `compress`            | Compress the file using a specified algorithm.              |
| `decompress`          | Decompress the file using a specified algorithm.            |
| `get_members`         | Get a list of members in the archive.                       |
| `get_member`          | Get metadata for a specific member in the archive.          |
| `add_member`          | Add a file to the archive.                                  |
| `remove_member`       | Remove a file from the archive.                             |
| `extract_all`         | Extract all members of the archive.                         |
| `extract_member`      | Extract a specific member from the archive.                 |
| `remove_all`          | Remove all members from the archive by deleting the archive.|
| `print_members`       | Print all members of the archive.                           |


### Archive

The `Archive` class is responsible for interacting with archive files (e.g., TAR, ZIP, SEVEN_ZIP). It provides methods for managing and extracting files within an archive.

| Method/Property       | Description                                                   |
|-----------------------|---------------------------------------------------------------|
| `path`                | Returns the path of the archive.                              |
| `size`                | Returns the size of the archive in bytes.                     |
| `get_members`         | Get a list of members in the archive.                         |
| `get_member`          | Get metadata for a specific member in the archive.            |
| `add_member`          | Add a new file to the archive.                                |
| `remove_member`       | Remove a file from the archive.                               |
| `extract_member`      | Extract a specific member from the archive.                   |
| `extract_all`         | Extract all members of the archive.                           |
| `remove_all`          | Remove all members by deleting the archive.                   |
| `print_members`       | Print a list of all members in the archive.                   |

### Compression

The `Compression` class handles file compression and decompression using popular algorithms such as GZIP, BZ2, LZ4, and XZ.

| Method/Property       | Description                                                   |
|-----------------------|---------------------------------------------------------------|
| `path`                | Returns the path of the compressed file.                      |
| `is_compressed`       | Check if the file is compressed using a specified algorithm.  |
| `uncompressed_size`   | Get the uncompressed size of the file.                        |
| `compressed_size`     | Get the compressed size of the file.                          |
| `compression_ratio`   | Calculate the compression ratio (uncompressed vs compressed). |
| `compress`            | Compress the file using a specified algorithm.                |
| `decompress`          | Decompress the file using a specified algorithm.              |


## Usage

### Example Usage with Archive

```python
from filepack.archive import Archive
import tempfile
from pathlib import Path

# Create a temporary directory for the archive
with tempfile.TemporaryDirectory() as temporary_directory:
    temporary_directory = Path(temporary_directory)
    new_archive_path = temporary_directory / "some-archive.tar"

    # Initialize Archive with a new archive file path
    archive = Archive(path=new_archive_path)

    # Get a list of members in the archive (initially empty)
    print([member.name for member in archive.get_members()])
    # Output: []

    # Create a new file to add to the archive
    new_file_path = temporary_directory / "new_file.txt"
    new_file_path.write_text("New File")
    
    # Add the new file to the archive
    archive.add_member(member_path=new_file_path)

    # List archive members after adding the file
    print([member.name for member in archive.get_members()])
    # Output: ['new_file.txt']

    # Create a new directory to extract the file
    new_dir_path = temporary_directory / "new_dir"
    new_dir_path.mkdir(exist_ok=True)

    # Extract the specific member (new_file.txt) to the new directory
    archive.extract_member(
        member_name=new_file_path.name, 
        target_directory_path=new_dir_path
    )

    # Verify if the file was extracted correctly
    print(new_file_path.name in (file.name for file in new_dir_path.iterdir()))
    # Output: True
    
    # Remove the file from the archive
    archive.remove_member(member_name=new_file_path.name)

    # Check if the archive is empty after removal
    print([member.name for member in archive.get_members()])
    # Output: []
```

### Example Usage with Compression

```python
## Example Usage with Compression

from filepack.compression import Compression
import tempfile
from pathlib import Path

# Create a temporary directory for the files
with tempfile.TemporaryDirectory() as temporary_directory:
    temporary_directory = Path(temporary_directory)
    
    # Create a new file to compress
    new_file_path = temporary_directory / "new_file.txt"
    new_file_path.write_text("This is a test file for compression.")

    # Initialize Compression with the file path
    compression = Compression(path=new_file_path)

    # Compress the file using gzip
    compressed_file_path = compression.compress(compression_algorithm="gz", in_place=True)
    
    # Check the path of the compressed file
    print(compressed_file_path.name)
    # Output: new_file.txt.gz

    # Check if the file is compressed
    print(compression.is_compressed(compression_algorithm="gz"))
    # Output: True

    # Get the compression ratio
    ratio = compression.compression_ratio(compression_algorithm="gz")
    print(f"Compression ratio: {ratio}")
    # Output: Compression ratio: <ratio_value>

    # Decompress the file
    decompressed_file_path = compression.decompress(compression_algorithm="gz", in_place=True)

    # Verify the decompressed file is the same as the original
    print(decompressed_file_path)
    # Output: path/to/new_file.txt
    
    print(decompressed_file_path.read_text() == "This is a test file for compression.")
    # Output: True
```

### Working with FilePack Unified Interface

```python
from filepack import FilePack
import tempfile
from pathlib import Path

# Set the compression algorithm and archive extension
compression_algorithm = "gz"
archive_extension = "tar"

# Create a temporary directory to work with
with tempfile.TemporaryDirectory() as temporary_directory:
    temporary_directory = Path(temporary_directory)

    # Define the path for the new archive file (e.g., new_archive.tar)
    new_archive_path = temporary_directory / f"new_archive.{archive_extension}"

    # Initialize FilePack with the archive path
    fp = FilePack(path=new_archive_path)

    print([member.name for member in fp.get_members()])
    # Output: []

    # Create a new file to be added to the archive
    new_file_path = temporary_directory / "new_file.txt"
    new_file_path.write_text("This is a test file for compression.")

    # Add the new file to the archive
    fp.add_member(member_path=new_file_path)

    print([member.name for member in fp.get_members()])
    # Output: [new_file.txt]

    # Define the path for the compressed archive (e.g., new_archive.tar.gz)
    compressed_archive_path = (
        new_archive_path.parent
        / f"{new_archive_path.name}.{compression_algorithm}"
    )

    # Compress the archive using gzip and replace the original file (in_place=True)
    fp.compress(
        target_path=compressed_archive_path,
        compression_algorithm=compression_algorithm,
        in_place=True,
    )

    # Check if the archive is now compressed
    print(fp.is_compressed(compression_algorithm=compression_algorithm))
    # Output: True

    # Decompress the archive and replace the compressed file with the decompressed one
    fp.decompress(
        target_path=new_archive_path,
        compression_algorithm=compression_algorithm,
        in_place=True,
    )

    # Check if the archive is still compressed after decompression
    print(fp.is_compressed(compression_algorithm=compression_algorithm))
    # Output: False

    # Define the target directory where the extracted file will be saved
    target_file_directory_path = temporary_directory / "target_dir"
    target_file_directory_path.mkdir(exist_ok=True)

    # Extract the specific file from the archive to the target directory
    fp.extract_member(
        member_name=new_file_path.name,
        target_directory_path=target_file_directory_path,
    )

    # Verify that the extracted file exists in the target directory
    print([file.name for file in target_file_directory_path.iterdir() if file.name == new_file_path.name][0])
    # Output: new_file.txt
```

## Error Handling

`filepack` has built-in error handling mechanisms. It raises user-friendly exceptions for common errors, allowing you to handle them gracefully in your application.

## Contributing

Interested in contributing to `filepack`? [See our contribution guide](CONTRIBUTING.md).

