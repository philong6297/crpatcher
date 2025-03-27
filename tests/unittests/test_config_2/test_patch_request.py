# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pathlib import Path
from typing import NamedTuple

import pytest

from crpatcher.config_2 import PatchRequest
from tests.base.input_data import Input, InputType
from tests.base.pytest_cases import (
    pytest_cases_fixture,
    pytest_cases_fixture_ref,
    pytest_cases_parametrize,
    pytest_cases_parametrize_with_cases,
)


class PathTestInput(NamedTuple):
    path: Path
    base_dir: Path
    use_absolute_path: bool


@pytest_cases_fixture(scope="class")
@pytest_cases_parametrize("is_exist", [True, False])
@pytest_cases_parametrize("is_absolute", [True, False])
def fixt_repo_dir(is_exist: bool, is_absolute: bool) -> Input[PathTestInput]:
    pass
