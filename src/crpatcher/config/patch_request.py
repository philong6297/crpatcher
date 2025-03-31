# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path
from typing import Any, final

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from crpatcher.base import CRPATCHER_STRICT_CONFIG, is_filename_only
from crpatcher.config.program_context import ProgramContext


@final
class PatchRequest(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()

    # must exist
    repo_dir: Path = Field()
    # must exist
    patch_dir: Path = Field()

    # same as .gitignore format. Used to ignore matched modified files in the repo_dir when generating patches
    ignore_patterns: list[str] = Field(default_factory=list)
    # list of patch file names to keep in the patch_dir. CRPatcher will not remove these files if exist.
    # Only accept file name, not path.
    keep_patch_files: list[str] = Field(default_factory=list)

    @cached_property
    def ignore_pattern_matcher(self) -> PathSpec | None:
        if not self.ignore_patterns:
            return None
        # unfortunatelly, PathSpec.from_lines() wont raise error with invalid patterns
        return PathSpec.from_lines(GitWildMatchPattern, self.ignore_patterns)

    @staticmethod
    def create_with_context(
        program_context: ProgramContext | None, **kwargs: Any
    ) -> PatchRequest:
        return PatchRequest.model_validate(kwargs, context=program_context)

    @field_validator("repo_dir", "patch_dir", mode="after")
    @classmethod
    def _resolve_directory(cls, dir_field: Path, info: ValidationInfo) -> Path:
        # if there is a valid ProgramContext, base_dir is already valid. Dont need to check its existence
        # if there is a valid ProgramContext, base_dir is already valid. Dont need to check its existence
        base_dir = (
            info.context.config_file.parent
            if isinstance(info.context, ProgramContext)
            else None
        )

        if dir_field.is_absolute():
            if not dir_field.is_dir():
                raise ValueError(f'Directory not found: "{dir_field.as_posix()}"')
            return dir_field

        if base_dir is None:
            raise ValueError(f'Unable to resolve "{dir_field.as_posix()}"')

        try:
            resolved_dir = (base_dir / dir_field).resolve(strict=True)
        except OSError as e:
            raise ValueError(
                f'Cannot resolve directory "{dir_field.as_posix()}".{os.linesep}Error: {e}'
            ) from e
        return resolved_dir

    @field_validator("keep_patch_files", mode="after")
    @classmethod
    def _validate_keep_patch_files(cls, v: list[str]) -> list[str]:
        for file_name in v:
            if not is_filename_only(file_name):
                raise ValueError(
                    f'Invalid file name when validating keep_patch_files: "{file_name}".'
                    f"Only file name is allowed, not path"
                )
        return v
