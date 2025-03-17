from __future__ import annotations

import codecs
import hashlib
import logging
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Dict, Type, TypeVar

__all__ = [
    "calculate_file_checksum",
    "validate_dict_keys_match_dataclass",
    "exists_encoding",
]

_logger = logging.getLogger(__name__)


def exists_encoding(enc: str) -> bool:
    try:
        codecs.lookup(enc)
    except LookupError:
        return False
    return True


def calculate_file_checksum(file_path: Path, buffer_size: int = 8192) -> str:
    # Input validation
    if not file_path.exists():
        raise ValueError(f"File does not exist: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    try:
        checksum_generator = hashlib.new("sha256")
        with file_path.open("rb") as file:
            while chunk := file.read(buffer_size):
                checksum_generator.update(chunk)
        return checksum_generator.hexdigest()
    except Exception as err:
        raise RuntimeError(
            f"Checksum calculation failed for {file_path}: {err}"
        ) from err


T = TypeVar("T")


def validate_dict_keys_match_dataclass(
    data: Dict[str, Any], dataclass_type: Type[T]
) -> bool:
    if not is_dataclass(dataclass_type):
        return False

    # Get all field names from the dataclass
    dataclass_field_names = {field.name for field in fields(dataclass_type)}

    # Check if all dataclass fields are present in the dictionary
    if not dataclass_field_names.issubset(data.keys()):
        return False

    return True
