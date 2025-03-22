# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.


import itertools
from pathlib import Path
from typing import Optional

import pytest

from crpatcher.config import ProgramContext
from tests.base.input_data import Input, InputType
from tests.unittests.test_config.helper import *


@pytest.fixture(scope="class")
def crpatcher_all_request_test_inputs_fixt(
    crpatcher_existing_empty_file_fixt: Path,
    crpatcher_base_dir_fixt: Path,
    crpatcher_existing_empty_dir_fixt: Path,
    crpatcher_non_existent_dir_fixt: Path,
) -> list[RequestTestInput]:
    program_context_datas: list[Input[Optional[ProgramContext]]] = [
        Input(
            data=ProgramContext(config_file=crpatcher_existing_empty_file_fixt),
            type=InputType.CUSTOM,
        ),  # build validation context from existing file
        Input(data=None, type=InputType.CUSTOM),  # no validation context
    ]

    PATH_CONDITIONS = list(
        itertools.product(
            [
                True,  # exist path
                False,  # non-exist path
            ],
            [
                True,  # use absolute path
                False,  # use relative path
            ],
        )
    )

    def _make_path_input(
        use_valid_path: bool,
        use_absolute_path: bool,
    ) -> Input[PathTestInput]:
        path_value = (
            crpatcher_existing_empty_dir_fixt
            if use_valid_path
            else crpatcher_non_existent_dir_fixt
        )

        return Input(
            data=PathTestInput(
                path=(
                    path_value
                    if use_absolute_path
                    else path_value.relative_to(crpatcher_base_dir_fixt)
                ),
                base_dir=crpatcher_base_dir_fixt,
                use_absolute_path=use_absolute_path,
            ),
            type=InputType.CUSTOM if use_valid_path else InputType.INVALID,
        )

    repo_dir_datas = [
        _make_path_input(use_valid_path, use_absolute_path)
        for use_valid_path, use_absolute_path in PATH_CONDITIONS
    ]

    # It is basically the same as repo_dir_datas, but we can keep it for clarity of generating of different patch dirs
    patch_dir_datas = [
        _make_path_input(use_valid_path, use_absolute_path)
        for use_valid_path, use_absolute_path in PATH_CONDITIONS
    ]

    keep_patch_files_datas = [
        Input[list[str]](),  # default
        Input(data=["patch1.patch", "patch2.patch"], type=InputType.CUSTOM),
        Input(
            data=["invalid/file_name.patch", "invalid/path/file"],
            type=InputType.INVALID,
        ),  # invalid, only accepts file name, not path
    ]

    ignore_patterns_datas = [
        Input[list[str]](),  # default
        Input(data=["*.patch"], type=InputType.CUSTOM),
        # currently, there is not invalid. invalid patterns will be ignored instead.
    ]

    return [
        RequestTestInput(
            repo_dir=repo_dir_data,
            patch_dir=patch_dir_data,
            program_context=program_context_data,
            keep_patch_files=keep_patch_files_data,
            ignore_patterns=ignore_patterns_data,
        )
        for repo_dir_data, patch_dir_data, program_context_data, keep_patch_files_data, ignore_patterns_data in itertools.product(
            repo_dir_datas,
            patch_dir_datas,
            program_context_datas,
            keep_patch_files_datas,
            ignore_patterns_datas,
        )
    ]
