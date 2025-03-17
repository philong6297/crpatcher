# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pathlib import Path

from pytest import TempPathFactory, fixture


@fixture(scope="class")
def crpatcher_test_base_dir(tmp_path_factory: TempPathFactory) -> Path:
    dir = tmp_path_factory.getbasetemp().joinpath("crpatcher_test_base_dir")
    dir.mkdir(parents=True, exist_ok=True)
    return dir


@fixture(scope="class")
def crpatcher_existing_empty_dir(crpatcher_test_base_dir: Path) -> Path:
    dir = crpatcher_test_base_dir.joinpath("existing_dir")
    dir.mkdir(parents=True, exist_ok=True)
    return dir


@fixture(scope="class")
def crpatcher_non_existent_dir(crpatcher_test_base_dir: Path) -> Path:
    dir = crpatcher_test_base_dir.joinpath("non_existent_dir")
    if dir.exists():
        raise FileExistsError(f"crpatcher_non_existent_dir={dir} already exists")
    return dir


@fixture(scope="class")
def crpatcher_existing_empty_file(crpatcher_test_base_dir: Path) -> Path:
    file = crpatcher_test_base_dir.joinpath("temp_file.txt")
    if not file.exists():
        file.touch()
    if not file.is_file():
        raise FileNotFoundError(f"crpatcher_existing_empty_file={file} is not a file")
    return file


@fixture(scope="class")
def crpatcher_non_existent_file(crpatcher_test_base_dir: Path) -> Path:
    file = crpatcher_test_base_dir.joinpath("non_existent_file.txt")
    if file.is_file():
        raise FileExistsError(f"crpatcher_non_existent_file={file} already exists")
    return file
