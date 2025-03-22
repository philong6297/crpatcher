# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

from typing import final

from pydantic import BaseModel, Field, field_validator

from crpatcher.base import CRPATCHER_STRICT_CONFIG, exists_encoding


@final
class PatchInfoOption(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()
    version: int = Field(
        default=1,
        ge=1,
    )
    encoding: str = Field(
        default="utf-8",
    )
    ext: str = Field(
        default="patchinfo",
        pattern=r"^\w+$",  # matches all alphanumeric characters and _
    )

    @field_validator("encoding", mode="after")
    def _validate_supported_encoding(cls, v: str) -> str:
        if not exists_encoding(v):
            raise ValueError(f"Unsupported encoding: {v}")
        return v
