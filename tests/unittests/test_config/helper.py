# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pathlib import Path
from typing import Any, NamedTuple

from crpatcher.config import PatchFileOption, PatchRequest, ProgramContext
from tests.base.input_data import Input, InputType


class PathData(NamedTuple):
    path: Path
    base_dir: Path
    use_absolute_path: bool


class RequestTestInput(NamedTuple):
    repo_dir: Input[PathData]
    patch_dir: Input[PathData]
    keep_patch_files: Input[list[str]]
    ignore_patterns: Input[list[str]]
    program_context: Input[ProgramContext | None]

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

        repo_dir_data: PathData = self.repo_dir.safe_data
        patch_dir_data: PathData = self.patch_dir.safe_data

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


class PatchFileOptionTestInput(NamedTuple):
    extension: Input[str]
    name_separator: Input[str]
    encoding: Input[str]

    @property
    def get_input_type(self) -> InputType:
        if (
            self.extension.type == InputType.INVALID
            or self.name_separator.type == InputType.INVALID
            or self.encoding.type == InputType.INVALID
        ):
            return InputType.INVALID

        if (
            self.extension.type == InputType.DEFAULT
            and self.name_separator.type == InputType.DEFAULT
            and self.encoding.type == InputType.DEFAULT
        ):
            return InputType.DEFAULT

        return InputType.CUSTOM

    def build_patch_file_option(self) -> PatchFileOption:
        if self.get_input_type == InputType.INVALID:
            raise ValueError(
                "PatchFileOptionTestInput is invalid. Cannot build PatchFileOption."
            )

        kwargs: dict[str, Any] = {}

        if self.extension.type != InputType.DEFAULT:
            kwargs["extension"] = self.extension.safe_data

        if self.name_separator.type != InputType.DEFAULT:
            kwargs["name_separator"] = self.name_separator.safe_data

        if self.encoding.type != InputType.DEFAULT:
            kwargs["encoding"] = self.encoding.safe_data

        return PatchFileOption(**kwargs)
