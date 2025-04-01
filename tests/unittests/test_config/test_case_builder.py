# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import itertools
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel

from crpatcher.base.util import CRPATCHER_STRICT_CONFIG
from crpatcher.config import ProgramContext
from tests.base.input_data import Input, InputType
from tests.unittests.test_config.helper import (
    PatchFileOptionTestInput,
    PathData,
    RequestTestInput,
)


class _PatchRequestTestCaseBuilder(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()

    @cached_property
    def REPO_DIR_CONSTRUCTION_TEST_CASES(self) -> list[tuple[bool, bool]]:
        return list(
            itertools.product(
                [True, False],  # is existing path
                [True, False],  # use absolute path
            )
        )

    @cached_property
    def REPO_DIR_CONSTRUCTION_TEST_CASE_IDS(self) -> list[str]:
        return [
            f"existing_path={is_existing_path};use_absolute_path={use_absolute_path}"
            for is_existing_path, use_absolute_path in self.REPO_DIR_CONSTRUCTION_TEST_CASES
        ]

    def build_repo_dir(
        self,
        *,
        use_valid_path: bool,
        use_absolute_path: bool,
        existing_empty_dir: Path,
        non_existent_dir: Path,
        base_dir: Path,
    ):
        return _make_dir_data(
            use_valid_path=use_valid_path,
            use_absolute_path=use_absolute_path,
            existing_empty_dir=existing_empty_dir,
            non_existent_dir=non_existent_dir,
            base_dir=base_dir,
        )

    @cached_property
    def PATCH_DIR_CONSTRUCTION_TEST_CASES(self) -> list[tuple[bool, bool]]:
        return list(
            itertools.product(
                [True, False],  # is existing path
                [True, False],  # use absolute path
            )
        )

    @cached_property
    def PATCH_DIR_CONSTRUCTION_TEST_CASE_IDS(self) -> list[str]:
        return [
            f"existing_path={is_existing_path};use_absolute_path={use_absolute_path}"
            for is_existing_path, use_absolute_path in self.PATCH_DIR_CONSTRUCTION_TEST_CASES
        ]

    def build_patch_dir(
        self,
        *,
        use_valid_path: bool,
        use_absolute_path: bool,
        existing_empty_dir: Path,
        non_existent_dir: Path,
        base_dir: Path,
    ):
        return _make_dir_data(
            use_valid_path=use_valid_path,
            use_absolute_path=use_absolute_path,
            existing_empty_dir=existing_empty_dir,
            non_existent_dir=non_existent_dir,
            base_dir=base_dir,
        )

    @cached_property
    def IGNORE_PATTERNS_CONSTRUCTION_TEST_CASES(self) -> list[Input[list[str]]]:
        return [
            Input(),  # default
            Input(data=["*.txt", "*.log", "*.py", "*.md"], type=InputType.CUSTOM),
            Input(
                data=["[invalid", "a-format]"], type=InputType.CUSTOM
            ),  # Invalid patterns, but wont raise error. See PatchRequest.ignore_pattern_matcher
        ]

    @cached_property
    def IGNORE_PATTERNS_CONSTRUCTION_TEST_CASE_IDS(self) -> list[str]:
        return [
            f"{desc}"
            for desc in [
                "default",
                "valid_patterns",
                "invalid_patterns_but_wont_raise_error",
            ]
        ]

    def build_ignore_patterns(self, input: Input[list[str]]):
        return input

    @cached_property
    def KEEP_PATCH_FILES_CONSTRUCTION_TEST_CASES(self) -> list[Input[list[str]]]:
        return [
            Input(),
            Input(data=["valid_name", "valid_name.txt"], type=InputType.CUSTOM),
            Input(data=["invalid_name/"], type=InputType.INVALID),
        ]

    @cached_property
    def KEEP_PATCH_FILES_CONSTRUCTION_TEST_CASE_IDS(self) -> list[str]:
        return [
            f"{input.type.name}"
            for input in self.KEEP_PATCH_FILES_CONSTRUCTION_TEST_CASES
        ]

    def build_keep_patch_files(self, input: Input[list[str]]):
        return input

    @cached_property
    def PROGRAM_CONTEXT_CONSTRUCTION_TEST_CASES(self) -> list[bool]:
        return [
            True,  # use context
            False,  # no context
        ]

    @cached_property
    def PROGRAM_CONTEXT_CONSTRUCTION_TEST_CASE_IDS(self) -> list[str]:
        return [
            f"has_context={has_context}"
            for has_context in self.PROGRAM_CONTEXT_CONSTRUCTION_TEST_CASES
        ]

    def build_program_context(
        self, *, has_context: bool, file: Path
    ) -> Input[ProgramContext | None]:
        if has_context:
            return Input(
                data=ProgramContext(config_file=file),
                type=InputType.CUSTOM,
            )

        return Input(data=None, type=InputType.CUSTOM)  # no validation context

    def build_all_requests(
        self,
        *,
        existing_empty_file: Path,
        existing_empty_dir: Path,
        non_existent_dir: Path,
        base_dir: Path,
    ) -> list[RequestTestInput]:
        return [
            self.build_request_test_input(
                repo_dir_arg=repo_dir_arg,
                patch_dir_arg=patch_dir_arg,
                ignore_patterns_arg=ignore_patterns_arg,
                keep_patch_files_arg=keep_patch_files_arg,
                program_context_arg=program_context_arg,
                existing_empty_file=existing_empty_file,
                existing_empty_dir=existing_empty_dir,
                non_existent_dir=non_existent_dir,
                base_dir=base_dir,
            )
            for (
                repo_dir_arg,
                patch_dir_arg,
                ignore_patterns_arg,
                keep_patch_files_arg,
                program_context_arg,
            ) in itertools.product(
                self.REPO_DIR_CONSTRUCTION_TEST_CASES,
                self.PATCH_DIR_CONSTRUCTION_TEST_CASES,
                self.IGNORE_PATTERNS_CONSTRUCTION_TEST_CASES,
                self.KEEP_PATCH_FILES_CONSTRUCTION_TEST_CASES,
                self.PROGRAM_CONTEXT_CONSTRUCTION_TEST_CASES,
            )
        ]

    def build_request_test_input(
        self,
        *,
        repo_dir_arg: tuple[bool, bool],
        patch_dir_arg: tuple[bool, bool],
        ignore_patterns_arg: Input[list[str]],
        keep_patch_files_arg: Input[list[str]],
        program_context_arg: bool,
        existing_empty_file: Path,
        existing_empty_dir: Path,
        non_existent_dir: Path,
        base_dir: Path,
    ) -> RequestTestInput:
        repo_dir = self.build_repo_dir(
            use_valid_path=repo_dir_arg[0],
            use_absolute_path=repo_dir_arg[1],
            existing_empty_dir=existing_empty_dir,
            non_existent_dir=non_existent_dir,
            base_dir=base_dir,
        )

        patch_dir = self.build_patch_dir(
            use_valid_path=patch_dir_arg[0],
            use_absolute_path=patch_dir_arg[1],
            existing_empty_dir=existing_empty_dir,
            non_existent_dir=non_existent_dir,
            base_dir=base_dir,
        )

        ignore_patterns = self.build_ignore_patterns(ignore_patterns_arg)

        keep_patch_files = self.build_keep_patch_files(keep_patch_files_arg)

        program_context = self.build_program_context(
            has_context=program_context_arg,
            file=existing_empty_file,
        )

        return RequestTestInput(
            repo_dir=repo_dir,
            patch_dir=patch_dir,
            ignore_patterns=ignore_patterns,
            keep_patch_files=keep_patch_files,
            program_context=program_context,
        )


def _make_dir_data(
    *,
    use_valid_path: bool,
    use_absolute_path: bool,
    existing_empty_dir: Path,
    non_existent_dir: Path,
    base_dir: Path,
) -> Input[PathData]:
    path_value = existing_empty_dir if use_valid_path else non_existent_dir

    return Input(
        data=PathData(
            path=(
                path_value if use_absolute_path else path_value.relative_to(base_dir)
            ),
            base_dir=base_dir,
            use_absolute_path=use_absolute_path,
        ),
        type=InputType.CUSTOM if use_valid_path else InputType.INVALID,
    )


class _PatchFileOptionTestCaseBuilder(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()

    @cached_property
    def EXTENSION_CONSTRUCTION_TEST_CASES(self) -> list[Input[str]]:
        return [
            Input(),  # default
            Input(data="patch-1", type=InputType.CUSTOM),
            Input(data="", type=InputType.INVALID),
            Input(data="mp3!invalid", type=InputType.INVALID),
        ]

    @cached_property
    def EXTENSION_CONSTRUCTION_TEST_CASE_IDS(self) -> list[str]:
        return ["default", "valid", "invalid_empty", "invalid_char"]

    @cached_property
    def NAME_SEPARATOR_CONSTRUCTION_TEST_CASES(self) -> list[Input[str]]:
        return [
            Input(),  # default
            Input(data="patch-1", type=InputType.CUSTOM),
            Input(data="", type=InputType.CUSTOM),
            Input(data="mp3!invalid", type=InputType.INVALID),
        ]

    @cached_property
    def NAME_SEPARATOR_CONSTRUCTION_TEST_CASE_IDS(self) -> list[str]:
        return ["default", "valid", "valid_empty", "invalid_char"]

    @cached_property
    def ENCODING_CONSTRUCTION_TEST_CASES(self) -> list[Input[str]]:
        return [
            Input(),  # default
            Input(data="utf-16", type=InputType.CUSTOM),
            Input(data="", type=InputType.INVALID),
            Input(data="invalid-utf", type=InputType.INVALID),
        ]

    @cached_property
    def ENCODING_CONSTRUCTION_TEST_CASE_IDS(self) -> list[str]:
        return ["default", "valid", "invalid_empty", "invalid_encoding"]

    def build_patch_file_option_test_input(
        self,
        *,
        extension_arg: Input[str],
        name_separator_arg: Input[str],
        encoding_arg: Input[str],
    ) -> PatchFileOptionTestInput:
        return PatchFileOptionTestInput(
            extension=extension_arg,
            name_separator=name_separator_arg,
            encoding=encoding_arg,
        )


PATCH_REQUEST_TEST_CASE_BUILDER = _PatchRequestTestCaseBuilder()
PATCH_FILE_OPTION_TEST_CASE_BUILDER = _PatchFileOptionTestCaseBuilder()
