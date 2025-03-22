# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pathlib import Path

import pytest


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
def crpatcher_non_existent_file_fixt(crpatcher_base_dir_fixt: Path) -> Path:
    file = crpatcher_base_dir_fixt.joinpath("non_existent_file.txt").absolute()
    if file.is_file():
        raise FileExistsError(f"crpatcher_non_existent_file_fixt={file} already exists")
    return file
