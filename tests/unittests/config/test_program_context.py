# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from pathlib import Path

import pytest
from pydantic import ValidationError

from crpatcher.config import ProgramContext
from tests.base.input_data import Input, InputType


def test_program_context(
    crpatcher_existing_empty_file_fixt: Path,
    crpatcher_existing_empty_dir_fixt: Path,
    crpatcher_non_existent_file: Path,
) -> None:
    test_cases = [
        Input(
            data=crpatcher_existing_empty_file_fixt, type=InputType.CUSTOM
        ),  # Valid file
        Input(
            data=crpatcher_existing_empty_dir_fixt, type=InputType.INVALID
        ),  # Directory instead of file
        Input(
            data=crpatcher_non_existent_file, type=InputType.INVALID
        ),  # Non-existent file
    ]

    for case in test_cases:
        with pytest.raises(ValidationError) if case.is_invalid_data else nullcontext():
            context = ProgramContext(config_file=case.safe_data)
            if not case.is_invalid_data:
                assert context.config_file == case.safe_data
                assert context.config_file.is_file()
