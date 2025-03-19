# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, final

from pydantic import BaseModel, Field, ValidationInfo, field_serializer, field_validator

from crpatcher.config.program_validation_context import ProgramValidationContext
from crpatcher.config.util import CRPATCHER_STRICT_CONFIG

__all__ = ["RepositoryConfig"]


@final
class RepositoryConfig(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG
    repo_dir: Path = Field()
    patch_dir: Path = Field()

    @staticmethod
    def create_with_context(
        program_context: Optional[ProgramValidationContext], **kwargs: Any
    ) -> RepositoryConfig:
        return RepositoryConfig.model_validate(kwargs, context=program_context)

    @field_validator("repo_dir", "patch_dir", mode="after")
    @classmethod
    def _resolve_directory(cls, dir: Path, info: ValidationInfo) -> Path:
        # if there is a valid ProgramValidationContext, base_dir is already valid. Dont need to check its existence
        base_dir = (
            info.context.config_file.parent
            if isinstance(info.context, ProgramValidationContext)
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

    @field_serializer("repo_dir", "patch_dir")
    def _serialize_path(self, path: Path, _info: Any) -> str:
        return str(path)
