# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from pathlib import Path

import pytest
from pydantic import ValidationError

from crpatcher.config import ProgramValidationContext


class TestProgramValidationContext:
    @pytest.fixture(scope="class")
    def filepath_fixture(self, request: pytest.FixtureRequest) -> Path:
        return request.getfixturevalue(request.param)

    @pytest.mark.parametrize(
        ("filepath_fixture", "should_raise_error"),
        [
            # Valid file
            (
                "crpatcher_existing_empty_file",
                False,
            ),
            # Directory instead of file
            (
                "crpatcher_existing_empty_dir",
                True,
            ),
            # Non-existent file
            (
                "crpatcher_non_existent_file",
                True,
            ),
        ],
        indirect=["filepath_fixture"],
    )
    def test_program_validation_context(
        self,
        filepath_fixture: Path,
        should_raise_error: bool,
    ) -> None:
        with pytest.raises(ValidationError) if should_raise_error else nullcontext():
            context = ProgramValidationContext(config_file=filepath_fixture)
            if not should_raise_error:
                assert context.config_file == filepath_fixture
                assert context.config_file.is_file()
