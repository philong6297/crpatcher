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


class PathTestData(NamedTuple):
    path: Path
    base_dir: Path
    use_valid_path: bool
    use_absolute_path: bool


def _make_path_fixture(
    path_name: str,
) -> Callable[[Path, Path, Path, pytest.FixtureRequest], PathTestData]:
    PATH_CONDITIONS = itertools.product(
        [
            True,  # exist path
            False,  # non-exist path
        ],
        [
            True,  # use absolute path
            False,  # use relative path
        ],
    )

    def id_generator(condition: tuple[bool, bool]) -> str:
        use_valid_path, use_absolute_path = condition

        return (
            f"{path_name}_"
            f"{'valid' if use_valid_path else 'invalid'}_"
            f"{'absolute' if use_absolute_path else 'relative'}"
        )

    @pytest.fixture(
        scope="class",
        params=PATH_CONDITIONS,
        ids=id_generator,
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
            path=(
                test_dir
                if use_absolute_path
                else test_dir.relative_to(crpatcher_test_base_dir)
            ),
            base_dir=crpatcher_test_base_dir,
            use_valid_path=use_valid_path,
            use_absolute_path=use_absolute_path,
        )

    return _path_fixture


repo_dir_fixture = _make_path_fixture("repo_dir")
patch_dir_fixture = _make_path_fixture("patch_dir")


class TestRepositoryConfig:
    def test_direct_construction(
        self,
        repo_dir_fixture: PathTestData,
        patch_dir_fixture: PathTestData,
    ) -> None:
        # Test repository config construction behavior.
        # When using absolute paths (needs_context=False), direct constructor should work. Otherwise, it should raise ValidationError.

        needs_program_context = not (
            repo_dir_fixture.use_absolute_path and patch_dir_fixture.use_absolute_path
        )

        should_raise_error = any(
            [
                needs_program_context,  # Direct constructor should fail with relative paths
                (not repo_dir_fixture.use_valid_path),
                (not patch_dir_fixture.use_valid_path),
            ]
        )

        context = (
            pytest.raises(ValidationError) if should_raise_error else nullcontext()
        )

        with context:
            config = RepositoryConfig(
                repo_dir=repo_dir_fixture.path,
                patch_dir=patch_dir_fixture.path,
            )

            if not should_raise_error:
                # Verify paths are absolute and exist
                assert config.repo_dir.is_absolute()
                assert config.patch_dir.is_absolute()
                assert config.repo_dir.is_dir()
                assert config.patch_dir.is_dir()

                assert config.repo_dir == repo_dir_fixture.path
                assert config.patch_dir == patch_dir_fixture.path

    def test_class_construction_with_context(
        self,
        validation_context_fixture: Optional[ProgramValidationContext],
        repo_dir_fixture: PathTestData,
        patch_dir_fixture: PathTestData,
    ) -> None:
        # Test with RepositoryConfig.create_with_context.
        #
        # Any invalid path (use_valid_path=False) should raise ValidationError.
        # For relative paths, validation context must be present.

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

        context = (
            pytest.raises(ValidationError) if should_raise_error else nullcontext()
        )

        with context:
            config = RepositoryConfig.create_with_context(
                program_context=validation_context_fixture,
                repo_dir=repo_dir_fixture.path,
                patch_dir=patch_dir_fixture.path,
            )

            if not should_raise_error:
                # Verify paths are absolute and exist
                assert config.repo_dir.is_absolute()
                assert config.patch_dir.is_absolute()
                assert config.repo_dir.is_dir()
                assert config.patch_dir.is_dir()

                # Verify relative paths are resolved correctly

                if repo_dir_fixture.use_absolute_path:
                    assert config.repo_dir == repo_dir_fixture.path
                else:
                    assert config.repo_dir == repo_dir_fixture.base_dir.joinpath(
                        repo_dir_fixture.path
                    )

                if patch_dir_fixture.use_absolute_path:
                    assert config.patch_dir == patch_dir_fixture.path
                else:
                    assert config.patch_dir == patch_dir_fixture.base_dir.joinpath(
                        patch_dir_fixture.path
                    )
