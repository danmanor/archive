import pytest
from pathlib import Path


@pytest.fixture
def txt_file(tmp_path: Path) -> Path:
    txt_file_path = tmp_path / "new_file.txt"
    with open(txt_file_path, "w") as file:
        file.write("Hello World !")
    
    return txt_file_path
