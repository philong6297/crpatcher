# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

# WARN: this file is only meant to be included by test_crpatcher_config.py
# and should not be used as a standalone file.

from pathlib import Path
from typing import Any, NamedTuple, Optional

from crpatcher.config import (
    PatchFileOption,
    PatchInfoFileOption,
    PatchRequest,
    ProgramContext,
)
from tests.base.input_data import Input, InputType


class PatchFileOptionTestInput(NamedTuple):
    ext: str
    encoding: str
    replacement_separator: str

    def build_patch_file_opt(self) -> PatchFileOption:
        return PatchFileOption(
            encoding=self.encoding,
            replacement_separator=self.replacement_separator,
            ext=self.ext,
        )


class PatchInfoFileOptionTestInput(NamedTuple):
    version: int
    ext: str
    encoding: str

    def build_patchinfo_file_opt(self) -> PatchInfoFileOption:
        return PatchInfoFileOption(
            version=self.version,
            encoding=self.encoding,
            ext=self.ext,
        )


class PathTestInput(NamedTuple):
    path: Path
    base_dir: Path
    use_absolute_path: bool


class RequestTestInput(NamedTuple):
    repo_dir: Input[PathTestInput]
    patch_dir: Input[PathTestInput]
    keep_patch_files: Input[list[str]]
    ignore_patterns: Input[list[str]]
    program_context: Input[Optional[ProgramContext]]
    patch_file_opt: Input[PatchFileOptionTestInput]
    patchinfo_file_opt: Input[PatchInfoFileOptionTestInput]

    @property
    def is_valid(self) -> bool:
        # there is no default program_context, repo_dir or patch_dir. We always need to create it
        if (
            self.repo_dir.type != InputType.CUSTOM
            or self.patch_dir.type != InputType.CUSTOM
            or self.program_context.type != InputType.CUSTOM
        ):
            return False

        if (
            self.ignore_patterns.type == InputType.INVALID
            or self.keep_patch_files.type == InputType.INVALID
            or self.patch_file_opt.type == InputType.INVALID
            or self.patchinfo_file_opt.type == InputType.INVALID
        ):
            return False

        if self.construction_needs_program_context:
            # program_context is required
            return self.program_context.safe_data is not None

        return True

    @property
    def construction_needs_program_context(self) -> bool:
        # both directories are absolute paths, no need to use program_context
        return not (
            self.repo_dir.safe_data.use_absolute_path
            and self.patch_dir.safe_data.use_absolute_path
        )

    def build_patch_request(self) -> PatchRequest:
        if not self.is_valid:
            raise ValueError("RequestTestInput is invalid. Cannot build PatchRequest.")

        repo_dir_data: PathTestInput = self.repo_dir.safe_data
        patch_dir_data: PathTestInput = self.patch_dir.safe_data

        other_args: dict[str, Any] = {}

        if self.keep_patch_files.type != InputType.DEFAULT:
            other_args["keep_patch_files"] = self.keep_patch_files.safe_data

        if self.ignore_patterns.type != InputType.DEFAULT:
            other_args["ignore_patterns"] = self.ignore_patterns.safe_data

        if self.construction_needs_program_context:
            return PatchRequest.create_with_context(
                repo_dir=repo_dir_data.path,
                patch_dir=patch_dir_data.path,
                program_context=self.program_context.safe_data,
                **other_args,
            )

        return PatchRequest(
            repo_dir=repo_dir_data.path,
            patch_dir=patch_dir_data.path,
            **other_args,
        )
