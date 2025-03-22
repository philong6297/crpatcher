# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from pathlib import Path

import pytest
from pydantic import ValidationError

from crpatcher.config import ProgramContext
from tests.base.input_data import Input, InputType
from tests.base.pytest_cases import pytest_cases_parametrize_with_cases


class ConfigFileTestCases:
    def case_valid_use_existing_file(
        self, crpatcher_existing_empty_file_fixt: Path
    ) -> Input[Path]:
        return Input(
            data=crpatcher_existing_empty_file_fixt, type=InputType.CUSTOM
        )  # Valid file

    def case_invalid_use_directory(
        self, crpatcher_existing_empty_dir_fixt: Path
    ) -> Input[Path]:
        return Input(
            data=crpatcher_existing_empty_dir_fixt, type=InputType.INVALID
        )  # Directory instead of file

    def case_invalid_use_non_existent_file(
        self, crpatcher_non_existent_file_fixt: Path
    ) -> Input[Path]:
        return Input(
            data=crpatcher_non_existent_file_fixt, type=InputType.INVALID
        )  # Non-existent file


@pytest_cases_parametrize_with_cases(
    "config_file",
    cases=ConfigFileTestCases,
)
def test_program_context(config_file: Input[Path]) -> None:
    with (
        pytest.raises(ValidationError) if config_file.is_invalid_data else nullcontext()
    ):
        context = ProgramContext(config_file=config_file.safe_data)
        if not config_file.is_invalid_data:
            assert context.config_file == config_file.safe_data
            assert context.config_file.is_file()
