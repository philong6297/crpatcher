# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path
from typing import Any, Optional, Self, final

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from pydantic import (
    BaseModel,
    Field,
    ValidationInfo,
    field_serializer,
    field_validator,
    model_validator,
)

from crpatcher.base import CRPATCHER_STRICT_CONFIG, is_filename_only
from crpatcher.config.patch_file_option import PatchFileOption
from crpatcher.config.patchinfo_file_option import PatchInfoFileOption
from crpatcher.config.program_context import ProgramContext

__all__ = ["PatchRequest"]


@final
class PatchRequest(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()

    # must exist
    repo_dir: Path = Field()
    # must exist
    patch_dir: Path = Field()

    # same as .gitignore format. Used to ignore matched modified files in the repo_dir when generating patches
    ignore_patterns: list[str] = Field(default_factory=list)
    # list of patch file names to keep. CRPatcher will not remove these files if exist.
    # Only accept file name, not path.
    keep_patch_files: list[str] = Field(default_factory=list)

    patchinfo_file_opt: PatchInfoFileOption = Field(
        default_factory=PatchInfoFileOption,
    )
    patch_file_opt: PatchFileOption = Field(
        default_factory=PatchFileOption,
    )

    @cached_property
    def ignore_pattern_matcher(self) -> Optional[PathSpec]:
        if not self.ignore_patterns:
            return None
        try:
            return PathSpec.from_lines(GitWildMatchPattern, self.ignore_patterns)
        except Exception as e:
            # TODO(longlp): add error message
            raise e

    @staticmethod
    def create_with_context(
        program_context: Optional[ProgramContext], **kwargs: Any
    ) -> PatchRequest:
        return PatchRequest.model_validate(kwargs, context=program_context)

    @model_validator(mode="after")
    def _validate_patch_dirs(self) -> Self:
        # validate each patch dir:
        # 1. no non-file: symlink, sub dir
        # 2. no file with wrong extension

        for file in self.patch_dir.iterdir():
            if not file.is_file():
                raise ValueError(
                    f"patch directory {self.patch_dir.as_posix()} is dirty:{os.linesep}"
                    f"contains non-file: {file.as_posix()}"
                )
            if file.suffix != f".{self.patch_file_opt.ext}":
                raise ValueError(
                    f"patch directory {self.patch_dir.as_posix()} is dirty:{os.linesep}"
                    f"contains patch file with wrong extension: {file.as_posix()}.{os.linesep}"
                    f"Expected extension: {self.patch_file_opt.ext}"
                )

        return self

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
