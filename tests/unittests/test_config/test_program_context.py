# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from pathlib import Path

import pytest
from pydantic import ValidationError

from crpatcher.config import ProgramContext
from tests.base.input_data import InputType


def test_program_context(
    fixt_crpatcher_existing_empty_dir: Path,
    fixt_crpatcher_non_existent_file: Path,
    fixt_crpatcher_existing_empty_file: Path,
):
    test_cases = [
        (
            fixt_crpatcher_existing_empty_file,
            InputType.CUSTOM,
        ),  # valid file
        (
            fixt_crpatcher_non_existent_file,
            InputType.INVALID,
        ),  # invalid, non-existent file
        (
            fixt_crpatcher_existing_empty_dir,
            InputType.INVALID,
        ),  # invalid, directory
    ]

    for input_data, input_type in test_cases:
        with (
            pytest.raises(ValidationError)
            if input_type == InputType.INVALID
            else nullcontext()
        ):
            context = ProgramContext(config_file=input_data)
            if input_type != InputType.INVALID:
                assert context.config_file == input_data
