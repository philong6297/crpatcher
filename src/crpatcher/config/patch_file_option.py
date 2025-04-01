# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pydantic import BaseModel, Field, field_validator

from crpatcher.base import CRPATCHER_STRICT_CONFIG, exists_encoding


class PatchFileOption(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()

    # only allow alphanumeric characters, dash and underscore. Do not allow empty string
    extension: str = Field(default="patch", pattern=r"^[\w-]+$")
    # only allow alphanumeric characters, dash and underscore. Allow empty string
    name_separator: str = Field(default="-", pattern=r"^[\w-]*$")
    encoding: str = Field(default="utf-8")

    @field_validator("encoding", mode="after")
    @classmethod
    def _validate_encoding(cls, v: str) -> str:
        if not exists_encoding(v):
            raise ValueError(f"Invalid encoding: {v}")
        return v
