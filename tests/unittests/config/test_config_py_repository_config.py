# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import itertools
from contextlib import nullcontext
from pathlib import Path
from typing import Callable, NamedTuple, Optional

import pytest
from pydantic import ValidationError

from crpatcher.config import ProgramValidationContext, RepositoryConfig


class PathTestData(NamedTuple):
    path: Path
    use_valid_path: bool
    use_absolute_path: bool


@pytest.fixture(
    scope="class",
    params=[
        True,  # build validation context from existing file
        False,  # no validation context
    ],
    ids=["valid_context", "invalid_context"],
)
def validation_context_fixture(
    crpatcher_existing_empty_file: Path, request: pytest.FixtureRequest
) -> Optional[ProgramValidationContext]:
    if request.param:
        return ProgramValidationContext(config_file=crpatcher_existing_empty_file)
    return None


def make_path_fixture(
    prefix: str,
) -> Callable[[Path, Path, Path, pytest.FixtureRequest], PathTestData]:
    """Create a fixture for testing paths with given prefix."""

    @pytest.fixture(
        scope="class",
        params=itertools.product(
            [
                True,  # exist path
                False,  # non-exist path
            ],
            [
                True,  # use absolute path
                False,  # use relative path
            ],
        ),
        ids=lambda param: f"{prefix}_{'valid' if param[0] else 'invalid'}_{'absolute' if param[1] else 'relative'}",
    )
    def _path_fixture(
        crpatcher_test_base_dir: Path,
        crpatcher_non_existent_dir: Path,
        crpatcher_existing_empty_dir: Path,
        request: pytest.FixtureRequest,
    ) -> PathTestData:
        use_valid_path, use_absolute_path = request.param

        test_dir = (
            crpatcher_existing_empty_dir
            if use_valid_path
            else crpatcher_non_existent_dir
        )

        return PathTestData(
            path=test_dir
            if use_absolute_path
            else test_dir.relative_to(crpatcher_test_base_dir),
            use_valid_path=use_valid_path,
            use_absolute_path=use_absolute_path,
        )

    return _path_fixture


repo_dir_fixture = make_path_fixture("repo_dir")
patch_dir_fixture = make_path_fixture("patch_dir")


def test_repository_config(
    validation_context_fixture: Optional[ProgramValidationContext],
    repo_dir_fixture: PathTestData,
    patch_dir_fixture: PathTestData,
) -> None:
    """Test repository config validation with different path combinations.

    Any invalid path (use_valid_path=False) should raise ValidationError.
    For relative paths, validation context must be present.
    """
    # Check if we need context (any relative path)
    needs_context = not (
        repo_dir_fixture.use_absolute_path and patch_dir_fixture.use_absolute_path
    )

    should_raise_error = any(
        [
            (needs_context and validation_context_fixture is None),
            (not repo_dir_fixture.use_valid_path),
            (not patch_dir_fixture.use_valid_path),
        ]
    )

    context = pytest.raises(ValidationError) if should_raise_error else nullcontext()

    with context:
        config = RepositoryConfig.model_validate({}, context=validation_context_fixture)

        if not should_raise_error:
            # Verify paths are absolute and exist
            assert config.repo_dir.is_absolute()
            assert config.patch_dir.is_absolute()
            assert config.repo_dir.is_dir()
            assert config.patch_dir.is_dir()

            # Verify relative paths are resolved correctly
            assert config.repo_dir == repo_dir_fixture.path.absolute()
            assert config.patch_dir == patch_dir_fixture.path.absolute()
            assert config.patch_dir == patch_dir_fixture.path.absolute()
