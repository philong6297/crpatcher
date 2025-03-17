# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Self, final

from pydantic import BaseModel, DirectoryPath, Field, ValidationInfo, model_validator

from crpatcher.base import NoPublicConstructor
from crpatcher.config.program_validation_context import ProgramValidationContext
from crpatcher.config.util import CRPATCHER_STRICT_CONFIG_DICT

__all__ = ["RepositoryConfig"]


@final
class RepositoryConfig(BaseModel, metaclass=NoPublicConstructor):
    model_config = CRPATCHER_STRICT_CONFIG_DICT
    repo_dir: Path = Field()
    patch_dir: Path = Field()

    @model_validator(mode="after")
    def _resolve_directories(self, info: ValidationInfo) -> Self:
        base_dir = (
            info.context.config_file.parent
            if isinstance(info.context, ProgramValidationContext)
            else None
        )

        # Create new instance with resolved paths, without validating
        return self.model_construct(
            repo_dir=_resolve_dir(self.repo_dir, base_dir),
            patch_dir=_resolve_dir(self.patch_dir, base_dir),
        )


def _resolve_dir(dir: Path, base_dir: Optional[DirectoryPath]) -> Path:
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
