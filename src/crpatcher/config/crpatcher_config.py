# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

# TODO: Add docstring and description for all fields

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field, FilePath, validate_call

from crpatcher.config.patch_config import PatchConfig
from crpatcher.config.patch_info_config import PatchInfoConfig
from crpatcher.config.program_validation_context import ProgramValidationContext
from crpatcher.config.repository_config import RepositoryConfig
from crpatcher.config.util import CRPATCHER_STRICT_CONFIG

__all__ = [
    "CRPatcherConfig",
]


class CRPatcherConfig(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG

    repositories: list[RepositoryConfig] = Field(
        default_factory=list,
    )
    patch_info_config: PatchInfoConfig = Field(
        default_factory=PatchInfoConfig,
    )
    patch_config: PatchConfig = Field(
        default_factory=PatchConfig,
    )

    @staticmethod
    # @validate_call(
    #     config=CRPATCHER_STRICT_CONFIG,
    #     validate_return=False,  # It is already validated
    # )
    def create_from_config_file(
        config_file: FilePath,  # make sure the file exist
    ) -> CRPatcherConfig:
        with config_file.open("rb") as f:
            config_data = tomllib.load(f)

        program_context = ProgramValidationContext(config_file=config_file)
        return CRPatcherConfig.model_validate(config_data, context=program_context)
