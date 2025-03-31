# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import itertools
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field

from crpatcher.base.util import CRPATCHER_STRICT_CONFIG
from crpatcher.config_2 import ProgramContext
from tests.base.input_data import Input, InputType
from tests.unittests.test_config_2.helper import PathData, RequestTestInput


class _ArgBuilder(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()

    @cached_property
    def REPO_DIR_ARGVALUES(self) -> list[tuple[bool, bool]]:
        return list(
            itertools.product(
                [True, False],  # is existing path
                [True, False],  # use absolute path
            )
        )

    @cached_property
    def REPO_DIR_IDS(self) -> list[str]:
        return [
            f"existing_path={is_existing_path};use_absolute_path={use_absolute_path}"
            for is_existing_path, use_absolute_path in self.REPO_DIR_ARGVALUES
        ]

    @classmethod
    def build_repo_dir(
        cls,
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
    def PATCH_DIR_ARGVALUES(self) -> list[tuple[bool, bool]]:
        return list(
            itertools.product(
                [True, False],  # is existing path
                [True, False],  # use absolute path
            )
        )

    @cached_property
    def PATCH_DIR_IDS(self) -> list[str]:
        return [
            f"existing_path={is_existing_path};use_absolute_path={use_absolute_path}"
            for is_existing_path, use_absolute_path in self.PATCH_DIR_ARGVALUES
        ]

    @classmethod
    def build_patch_dir(
        cls,
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
    def IGNORE_PATTERNS_ARGVALUES(self) -> list[Input[list[str]]]:
        return [
            Input(),  # default
            Input(data=["*.txt", "*.log", "*.py", "*.md"], type=InputType.CUSTOM),
            Input(
                data=["[invalid", "a-format]"], type=InputType.CUSTOM
            ),  # Invalid patterns, but wont raise error. See PatchRequest.ignore_pattern_matcher
        ]

    @cached_property
    def IGNORE_PATTERNS_IDS(self) -> list[str]:
        return [
            f"{desc}"
            for desc in [
                "default",
                "valid_patterns",
                "invalid_patterns_but_wont_raise_error",
            ]
        ]

    @classmethod
    def build_ignore_patterns(cls, input: Input[list[str]]):
        return input

    @cached_property
    def KEEP_PATCH_FILES_ARGVALUES(self) -> list[Input[list[str]]]:
        return [
            Input(),
            Input(data=["valid_name", "valid_name.txt"], type=InputType.CUSTOM),
            Input(data=["invalid_name/"], type=InputType.INVALID),
        ]

    @cached_property
    def KEEP_PATCH_FILES_IDS(self) -> list[str]:
        return [f"{input.type.name}" for input in self.KEEP_PATCH_FILES_ARGVALUES]

    @classmethod
    def build_keep_patch_files(cls, input: Input[list[str]]):
        return input

    @cached_property
    def PROGRAM_CONTEXT_ARGVALUES(self) -> list[bool]:
        return [
            True,  # use context
            False,  # no context
        ]

    @cached_property
    def PROGRAM_CONTEXT_IDS(self) -> list[str]:
        return [
            f"has_context={has_context}"
            for has_context in self.PROGRAM_CONTEXT_ARGVALUES
        ]

    @classmethod
    def build_program_context(
        cls, *, has_context: bool, file: Path
    ) -> Input[ProgramContext | None]:
        if has_context:
            return Input(
                data=ProgramContext(config_file=file),
                type=InputType.CUSTOM,
            )

        return Input(data=None, type=InputType.CUSTOM)  # no validation context


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


ARG_BUILDER = _ArgBuilder()
