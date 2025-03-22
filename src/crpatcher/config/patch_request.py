# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, final

from pydantic import BaseModel, Field, ValidationInfo, field_serializer, field_validator

from crpatcher.base import is_filename_only
from crpatcher.config.program_context import ProgramContext
from crpatcher.config.util import CRPATCHER_STRICT_CONFIG

__all__ = ["PatchRequest"]


@final
class PatchRequest(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()
    repo_dir: Path = Field()
    patch_dir: Path = Field()
    # same as .gitignore format
    ignore_patterns: list[str] = Field(default_factory=list)
    # list of patch file names to keep. CRPatcher will not remove these files if exist.
    # Only accept file name, not path.
    keep_patch_files: list[str] = Field(default_factory=list)

    @staticmethod
    def create_with_context(
        program_context: Optional[ProgramContext], **kwargs: Any
    ) -> PatchRequest:
        return PatchRequest.model_validate(kwargs, context=program_context)

    @field_validator("keep_patch_files", mode="after")
    @classmethod
    def _validate_keep_patch_files(cls, v: list[str]) -> list[str]:
        for file_name in v:
            if not is_filename_only(Path(file_name)):
                raise ValueError(
                    f'Invalid file name when validating keep_patch_files: "{file_name}".'
                    f"Only file name is allowed, not path"
                )
        return v

    @field_validator("repo_dir", "patch_dir", mode="after")
    @classmethod
    def _resolve_directory(cls, dir: Path, info: ValidationInfo) -> Path:
        # if there is a valid ProgramContext, base_dir is already valid. Dont need to check its existence
        base_dir = (
            info.context.config_file.parent
            if isinstance(info.context, ProgramContext)
            else None
        )

        if dir.is_absolute():
            if not dir.is_dir():
                raise ValueError(f'Directory not found: "{dir.as_posix()}"')
            return dir

        if base_dir is None:
            raise ValueError(
                f'Missing program validation context, used for resolving "{dir.as_posix()}"'
            )

        try:
            resolved_dir = base_dir.joinpath(dir).resolve(strict=True)
        except OSError as e:
            raise ValueError(
                f'Cannot resolve directory "{dir.as_posix()}".{os.linesep}Error: {e}'
            ) from e
        return resolved_dir

    @field_serializer("repo_dir", "patch_dir", check_fields=True, when_used="json")
    def _serialize_path(self, path: Path, _info: Any) -> str:
        return path.as_posix()
