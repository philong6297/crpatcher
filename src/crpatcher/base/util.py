# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import codecs
import hashlib
import logging
from pathlib import Path

__all__ = [
    "calculate_file_checksum",
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
