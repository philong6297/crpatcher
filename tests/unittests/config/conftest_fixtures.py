# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.


import itertools
from pathlib import Path
from typing import Optional

import pytest

from crpatcher.config import ProgramContext
from tests.base.input_data import Input, InputType
from tests.unittests.config.helper import *


@pytest.fixture(scope="class")
def crpatcher_base_dir_fixt(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.getbasetemp().joinpath("crpatcher_base_dir_fixt").absolute()
    dir.mkdir(parents=True, exist_ok=True)
    return dir


@pytest.fixture(scope="class")
def crpatcher_existing_empty_dir_fixt(crpatcher_base_dir_fixt: Path) -> Path:
    dir = crpatcher_base_dir_fixt.joinpath("existing_dir").absolute()
    dir.mkdir(parents=True, exist_ok=True)
    return dir


@pytest.fixture(scope="class")
def crpatcher_non_existent_dir_fixt(crpatcher_base_dir_fixt: Path) -> Path:
    dir = crpatcher_base_dir_fixt.joinpath("non_existent_dir").absolute()
    if dir.exists():
        raise FileExistsError(f"crpatcher_non_existent_dir_fixt={dir} already exists")
    return dir


@pytest.fixture(scope="class")
def crpatcher_existing_empty_file_fixt(crpatcher_base_dir_fixt: Path) -> Path:
    file = crpatcher_base_dir_fixt.joinpath("temp_file.txt").absolute()
    if not file.exists():
        file.touch()
    if not file.is_file():
        raise FileNotFoundError(
            f"crpatcher_existing_empty_file_fixt={file} is not a file"
        )
    return file


@pytest.fixture(scope="class")
def crpatcher_non_existent_file(crpatcher_base_dir_fixt: Path) -> Path:
    file = crpatcher_base_dir_fixt.joinpath("non_existent_file.txt").absolute()
    if file.is_file():
        raise FileExistsError(f"crpatcher_non_existent_file={file} already exists")
    return file


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

    return [
        RequestTestInput(
            repo_dir=repo_dir_data,
            patch_dir=patch_dir_data,
            program_context=program_context_data,
        )
        for repo_dir_data, patch_dir_data, program_context_data in itertools.product(
            repo_dir_datas, patch_dir_datas, program_context_datas
        )
    ]
