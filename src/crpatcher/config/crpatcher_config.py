# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

# TODO: Add docstring and description for all fields

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FilePath, validate_call

from crpatcher.config.patch_file_option import PatchFileOption
from crpatcher.config.patch_request import PatchRequest
from crpatcher.config.patchinfo_file_option import PatchInfoOption
from crpatcher.config.program_context import ProgramContext
from crpatcher.config.util import CRPATCHER_STRICT_CONFIG

__all__ = [
    "CRPatcherConfig",
]


class CRPatcherConfig(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()

    requests: list[PatchRequest] = Field(
        default_factory=list,
    )
    patchinfo_file_opt: PatchInfoOption = Field(
        default_factory=PatchInfoOption,
    )
    patch_file_opt: PatchFileOption = Field(
        default_factory=PatchFileOption,
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
