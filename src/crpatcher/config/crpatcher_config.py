# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from functools import cached_property

from pydantic import BaseModel, Field, FilePath, validate_call

from crpatcher.base import CRPATCHER_STRICT_CONFIG
from crpatcher.config.patch_request import PatchRequest
from crpatcher.config.program_context import ProgramContext


class CrPatcherConfig(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()

    requests: list[PatchRequest] = Field(default_factory=list)

    @cached_property
    def PATCH_FILE_EXTENSION(cls) -> str:
        return "patch"

    @cached_property
    def PATCH_FILE_ENCODING(cls) -> str:
        return "utf-8"

    @cached_property
    def PATCH_FILE_NAME_SEPARATOR(cls) -> str:
        return "-"

    @cached_property
    def PATCHINFO_FILE_EXTENSION(cls) -> str:
        return "patchinfo"

    @cached_property
    def PATCHINFO_FILE_ENCODING(cls) -> str:
        return "utf-8"

    @cached_property
    def PATCHINFO_FILE_VERSION(cls) -> int:
        return 1

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
        return CrPatcherConfig.model_validate_json(json_data, context=program_context)
