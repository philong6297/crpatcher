# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

# TODO: Add docstring and description for all fields

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Self

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    DirectoryPath,
    Field,
    FilePath,
    ValidationInfo,
    field_validator,
    model_validator,
)

from crpatcher.base import exists_encoding

__all__ = [
    "ProgramConfig",
    "PatchInfoConfig",
    "PatchConfig",
    "RepositoryConfig",
    "ProgramValidationContext",
]


class RepositoryConfig(BaseModel):
    model_config = _STRICT_CONFIG_DICT
    repo_dir: Path = Field()
    patch_dir: Path = Field()

    @model_validator(mode="after")
    def _resolve_directories(self, info: ValidationInfo) -> Self:
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


class ProgramConfig(BaseModel):
    model_config = _STRICT_CONFIG_DICT

    repositories: list[RepositoryConfig] = Field(
        default_factory=list,
    )
    patchinfo_config: PatchInfoConfig = Field(
        default_factory=PatchInfoConfig,
    )
    patch_config: PatchConfig = Field(
        default_factory=PatchConfig,
    )

    @classmethod
    def load(cls, config_file: Path | str) -> Self:
        config_file = Path(config_file)

        if not config_file.is_file():
            raise FileNotFoundError(f"File not found: {config_file}")

        with config_file.open("r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        program_context = ProgramValidationContext(config_file=config_file)
        return cls.model_validate(config_data, context=program_context)
