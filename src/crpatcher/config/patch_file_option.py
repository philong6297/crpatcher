# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

from typing import final

from pydantic import BaseModel, Field, field_validator

from crpatcher.base import exists_encoding
from crpatcher.config.util import CRPATCHER_STRICT_CONFIG


@final
class PatchFileOption(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()
    ext: str = Field(
        default="patch",
        pattern=r"^\w+$",  # matches all alphanumeric characters and _
    )
    encoding: str = Field(
        default="utf-8",
    )
    replacement_separator: str = Field(
        default="-",
        pattern=r"^[\w-]+$",  # matches all alphanumeric characters, _ and -
    )

    @field_validator("encoding", mode="after")
    def _validate_supported_encoding(cls, v: str) -> str:
        if not exists_encoding(v):
            raise ValueError(f"Unsupported encoding: {v}")
        return v
