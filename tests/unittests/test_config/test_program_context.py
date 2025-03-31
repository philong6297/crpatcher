# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from pathlib import Path

import pytest
from pydantic import ValidationError

from crpatcher.config import ProgramContext
from tests.base.input_data import InputType
from tests.base.pytest_cases import pytest_cases_fixture_ref, pytest_cases_parametrize


@pytest_cases_parametrize(
    argnames="input_data,input_type",
    argvalues=[
        (
            pytest_cases_fixture_ref("fixt_crpatcher_existing_empty_file"),
            InputType.CUSTOM,
        ),  # valid file
        (
            pytest_cases_fixture_ref("fixt_crpatcher_non_existent_file"),
            InputType.INVALID,
        ),  # invalid, non-existent file
        (
            pytest_cases_fixture_ref("fixt_crpatcher_existing_empty_dir"),
            InputType.INVALID,
        ),  # invalid, directory
    ],
    ids=["valid_file", "invalid_non_existent", "invalid_directory"],
)
def test_program_context(input_data: Path, input_type: InputType):
    with (
        pytest.raises(ValidationError)
        if input_type == InputType.INVALID
        else nullcontext()
    ):
        context = ProgramContext(config_file=input_data)
        if input_type != InputType.INVALID:
            assert context.config_file == input_data
