# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import codecs
import hashlib
import logging
from pathlib import Path
from typing import Annotated

from pydantic import ConfigDict, Field, FilePath, validate_call

__all__ = [
    "calculate_file_checksum_sha256",
    "exists_encoding",
    "is_filename_only",
    "CRPATCHER_STRICT_CONFIG",
]

_logger = logging.getLogger(__name__)


def CRPATCHER_STRICT_CONFIG() -> ConfigDict:
    return ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        strict=True,
        allow_inf_nan=False,
        validate_default=True,
    )


def exists_encoding(enc: str) -> bool:
    try:
        codecs.lookup(enc)
    except LookupError:
        return False
    return True


def is_filename_only(path: Path) -> bool:
    return (
        not path.parent or path.parent == Path(".")
    ) and path.name == path.as_posix()


@validate_call(
    config=CRPATCHER_STRICT_CONFIG(),
    validate_return=False,  # hexdigest always return a string
)
def calculate_file_checksum_sha256(
    file_path: FilePath,
    buffer_size: Annotated[int, Field(ge=1, default=8192)] = 8192,
) -> str:
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
