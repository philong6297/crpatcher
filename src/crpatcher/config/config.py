# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

# TODO: Add docstring and description for all fields

from __future__ import annotations

from pathlib import Path
from typing import Self

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    FilePath,
    ValidationInfo,
    model_validator,
    with_config,
)

__all__ = [
    "ProgramConfig",
    "PatchInfoConfig",
    "PatchConfig",
    "RepositoryConfig",
    "ProgramValidationContext",
]

_STRICT_CONFIG_DICT = ConfigDict(
    extra="forbid",
    frozen=True,
    validate_assignment=True,
    strict=True,
)


@with_config(_STRICT_CONFIG_DICT)
class ProgramValidationContext(BaseModel):
    config_file: FilePath = Field()


@with_config(_STRICT_CONFIG_DICT)
class PatchInfoConfig(BaseModel):
    version: int = Field(
        default=1,
        ge=1,
        allow_inf_nan=False,
    )
    encoding: str = Field(
        default="utf-8",
    )
    ext: str = Field(
        default="patchinfo",
        pattern=r"^\w+$",
    )


@with_config(_STRICT_CONFIG_DICT)
class PatchConfig(BaseModel):
    ext: str = Field(
        default="patch",
        pattern=r"^\w+$",
    )
    encoding: str = Field(
        default="utf-8",
    )
    replacement_separator: str = Field(
        default="-",
        pattern=r"^\w+$",
    )


@with_config(_STRICT_CONFIG_DICT)
class RepositoryConfig(BaseModel):
    repo_dir: Path = Field()
    patch_dir: Path = Field()

    @model_validator(mode="after")
    def _resolve_directories(self, info: ValidationInfo) -> Self:
        if not info.context or not isinstance(info.context, ProgramValidationContext):
            raise ValueError("Missing program validation context")

        config_file = info.context.config_file
        base_dir = config_file.parent

        # Resolve repo_dir, if it's not absolute, join it with config file's base directory
        if not self.repo_dir.is_absolute():
            self.repo_dir = base_dir.joinpath(self.repo_dir).resolve(strict=True)
        if not self.repo_dir.is_dir():
            raise ValueError(f"Repository directory not found: {self.repo_dir}")

        # Resolve patch_dir, if it's not absolute, join it with config file's base directory
        if not self.patch_dir.is_absolute():
            self.patch_dir = base_dir.joinpath(self.patch_dir).resolve(strict=True)
        if not self.patch_dir.is_dir():
            raise ValueError(f"Patch directory not found: {self.patch_dir}")

        return self


@with_config(_STRICT_CONFIG_DICT)
class ProgramConfig(BaseModel):
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
