# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import codecs
import hashlib
import logging
import os
import re

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


def is_filename_only(path_str: str) -> bool:
    # early stop
    if "/" in path_str or "\\" in path_str:
        return False
    pattern = (
        (
            r"^(?!^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?$)"  # Reserved names
            r'[^<>:"/\\|?*\x00-\x1F]+'  # Disallowed chars
            r'[^<>:"/\\|?*\x00-\x1F .]$'  # No trailing space/dot
        )  # Windows
        if os.name == "nt"
        else (
            r"^(?![.]{1,2}$)"  # Not "." or ".."
            r"[^/\x00]+"  # Disallow slash and null byte
            r"[^/\x00 ]$"  # No trailing space
        )  # POSIX
    )

    return re.match(pattern, path_str, re.IGNORECASE) is not None


@validate_call(
    config=CRPATCHER_STRICT_CONFIG(),
    validate_return=False,  # hexdigest always return a string
)
def calculate_file_checksum_sha256(
    file_path: FilePath,
    buffer_size: int = Field(ge=1, default=8192),
) -> str:
    checksum_generator = hashlib.new("sha256")
    with file_path.open("rb") as file:
        while chunk := file.read(buffer_size):
            checksum_generator.update(chunk)
    return checksum_generator.hexdigest()
