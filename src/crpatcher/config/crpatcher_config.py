# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

# TODO: Add docstring and description for all fields

from __future__ import annotations

import os
from typing import Self

from pydantic import BaseModel, Field, FilePath, model_validator, validate_call

from crpatcher.base import CRPATCHER_STRICT_CONFIG
from crpatcher.config.patch_file_option import PatchFileOption
from crpatcher.config.patch_request import PatchRequest
from crpatcher.config.patchinfo_file_option import PatchInfoFileOption
from crpatcher.config.program_context import ProgramContext

__all__ = [
    "CRPatcherConfig",
]


class CRPatcherConfig(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()

    requests: list[PatchRequest] = Field(
        default_factory=list,
    )

    @staticmethod
    @validate_call(
        config=CRPATCHER_STRICT_CONFIG(),
        validate_return=False,  # It is already validated
    )
    def create_from_config_file(
        config_file: FilePath,  # make sure the file exist
    ):  # No explicit return as per https://github.com/pydantic/pydantic/issues/11582
        json_data = config_file.read_bytes()

        program_context = ProgramContext(config_file=config_file)
        return CRPatcherConfig.model_validate_json(json_data, context=program_context)
