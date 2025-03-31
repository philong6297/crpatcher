# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pathlib import Path

import pytest


@pytest.fixture(scope="class")
def fixt_crpatcher_base_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = (tmp_path_factory.getbasetemp() / "fixt_crpatcher_base_dir").absolute()
    dir.mkdir(parents=True, exist_ok=True)
    return dir


@pytest.fixture(scope="class")
def fixt_crpatcher_existing_empty_dir(fixt_crpatcher_base_dir: Path) -> Path:
    dir = (fixt_crpatcher_base_dir / "existing_dir").absolute()
    dir.mkdir(parents=True, exist_ok=True)
    return dir


@pytest.fixture(scope="class")
def fixt_crpatcher_non_existent_dir(fixt_crpatcher_base_dir: Path) -> Path:
    dir = (fixt_crpatcher_base_dir / "non_existent_dir").absolute()
    if dir.exists():
        raise FileExistsError(f"fixt_crpatcher_non_existent_dir={dir} already exists")
    return dir


@pytest.fixture(scope="class")
def fixt_crpatcher_existing_empty_file(fixt_crpatcher_base_dir: Path) -> Path:
    file = (fixt_crpatcher_base_dir / "temp_file.txt").absolute()
    if not file.exists():
        file.touch()
    if not file.is_file():
        raise FileNotFoundError(
            f"fixt_crpatcher_existing_empty_file={file} is not a file"
        )
    return file


@pytest.fixture(scope="class")
def fixt_crpatcher_non_existent_file(fixt_crpatcher_base_dir: Path) -> Path:
    file = (fixt_crpatcher_base_dir / "non_existent_file.txt").absolute()
    if file.is_file():
        raise FileExistsError(f"fixt_crpatcher_non_existent_file={file} already exists")
    return file
