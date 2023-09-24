# filepack

A user-friendly interface for handling files, archives, and compressed files in Python.

## Features

- User-friendly interface for common file operations.
- Support for various archive types: TAR, ZIP, RAR, SEVEN_ZIP.
- Support for various compression types: GZIP, BZ2, LZ4, XZ.

## Installation
```
pip install filepack
```

## API Overview


### FilePack

| Method/Property       | Description                                     |
|-----------------------|-------------------------------------------------|
| `path`                | Returns the path of the file.                   |
| `suffix`              | Returns the file's suffix.                      |
| `is_compressed`       | Check if the file is compressed.                |
| `uncompressed_size`   | Get uncompressed size.                          |
| `compressed_size`     | Get compressed size.                            |
| `compression_ratio`   | Get compression ratio.                          |
| `compress`            | Compress the file.                              |
| `decompress`          | Decompress the file.                            |

### Archive

| Method/Property       | Description                                     |
|-----------------------|-------------------------------------------------|
| `path`                | Returns the path of the archive.                |
| `suffix`              | Returns the archive's suffix.                   |
| `extract_member`      | Extract a specific member.                      |
| `get_member`          | Get member's metadata                           |
| `get_members`         | Get a list of members metadata.                 |
| `add_member`          | Add a member to the archive.                    |
| `remove_member`       | Remove a member from the archive.               |
| `extract_all`         | Extract all members.                            |
| `remove_all`          | Remove all members from the archive.            |
| `print_members`       | Print all members.                              |

### Compression

| Method/Property       | Description                                     |
|-----------------------|-------------------------------------------------|
| `path`                | Returns the path of the compressed file.        |
| `suffix`              | Returns the file's suffix.                      |
| `uncompressed_size`   | Get uncompressed size.                          |
| `compressed_size`     | Get compressed size.                            |
| `compression_ratio`   | Get compression ratio.                          |
| `compress`            | Compress the file.                              |
| `decompress`          | Decompress the file.                            |
| `is_compressed`       | Check if the file is compressed.                |

## Usage

### Working with Archives

```
from filepack import FilePack


# if the given path can exist or not yet, but must refer to an archive.
file_pack = FilePack("path/to/your/archive/file")

# Extract a specific member
archive.extract_member(target_path="path/to/target/directory")

# Get a list of members
members = archive.get_members()

# Add a member to the archive
archive.add_member("path/to/member")

# Remove a member from the archive
archive.remove_member("name_of_member")

# Extract all members
archive.extract_all(target_path="path/to/target")

# Remove all members from the archive
archive.remove_all()

# Print all members
archive.print_members()
```
### Working with Compressions
```
from filepack import FilePack


# if the given path must exist, but can refer to a file which is compressed already or not.
file_pack = FilePack("path/to/your/existed/file")

# Compressed or not
is_compressed = file_pack.is_compressed(compression_algorithm="gz")

# Get uncompressed size
size = file_pack.uncompressed_size(compression_algorithm="gz")

# Compress and decompress files in place
new_path = file_pack.compress(compression_algorithm="gz") # with .gz
new_path = file_pack.decompress(compression_algorithm="gz") # without .gz

# Compress and decompress files into a different path
new_path = file_pack.compress(target_path="path/to/compressed/file", compression_algorithm="gz")
new_path = file_pack.decompress(target_path="path/to/uncompressed/file", compression_algorithm="gz")
```
### Working with Both
```
from filepack import FilePack


file_pack = FilePack("path/to/your/archive/file")

archive.add_member("path/to/member")
new_path = file_pack.compress(compression_algorithm="gz")
```

## Error Handling

`filepack` has built-in error handling mechanisms. It raises user-friendly exceptions for common errors, allowing you to handle them gracefully in your application.

## Contributing

Interested in contributing to `filepack`? [See our contribution guide](CONTRIBUTING.md).

