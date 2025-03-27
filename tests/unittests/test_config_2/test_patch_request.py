# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
from typing import Any, NamedTuple

import pytest
from pydantic import ValidationError

from crpatcher.config_2 import PatchRequest, ProgramContext
from tests.base.input_data import Input, InputType
from tests.base.pytest_cases import (
    pytest_cases_fixture,
    pytest_cases_fixture_ref,
    pytest_cases_parametrize,
    pytest_cases_parametrize_with_cases,
)


class PathData(NamedTuple):
    path: Path
    base_dir: Path
    use_absolute_path: bool


class RequestTestInput(NamedTuple):
    repo_dir: Input[PathData]
    patch_dir: Input[PathData]
    keep_patch_files: Input[list[str]]
    ignore_patterns: Input[list[str]]
    program_context: Input[ProgramContext | None]

    @property
    def is_valid(self) -> bool:
        # there is no default program_context, repo_dir or patch_dir. We always need to create it
        if (
            self.repo_dir.type != InputType.CUSTOM
            or self.patch_dir.type != InputType.CUSTOM
            or self.program_context.type != InputType.CUSTOM
        ):
            return False

        if (
            self.ignore_patterns.type == InputType.INVALID
            or self.keep_patch_files.type == InputType.INVALID
        ):
            return False

        if self.construction_needs_program_context:
            # program_context is required
            return self.program_context.safe_data is not None

        return True

    @property
    def construction_needs_program_context(self) -> bool:
        # both directories are absolute paths, no need to use program_context
        return not (
            self.repo_dir.safe_data.use_absolute_path
            and self.patch_dir.safe_data.use_absolute_path
        )

    def build_patch_request(self) -> PatchRequest:
        if not self.is_valid:
            raise ValueError("RequestTestInput is invalid. Cannot build PatchRequest.")

        repo_dir_data: PathData = self.repo_dir.safe_data
        patch_dir_data: PathData = self.patch_dir.safe_data

        other_args: dict[str, Any] = {}

        if self.keep_patch_files.type != InputType.DEFAULT:
            other_args["keep_patch_files"] = self.keep_patch_files.safe_data

        if self.ignore_patterns.type != InputType.DEFAULT:
            other_args["ignore_patterns"] = self.ignore_patterns.safe_data

        if self.construction_needs_program_context:
            return PatchRequest.create_with_context(
                repo_dir=repo_dir_data.path,
                patch_dir=patch_dir_data.path,
                program_context=self.program_context.safe_data,
                **other_args,
            )

        return PatchRequest(
            repo_dir=repo_dir_data.path,
            patch_dir=patch_dir_data.path,
            **other_args,
        )


def _make_dir_data(
    *,
    use_valid_path: bool,
    use_absolute_path: bool,
    existing_empty_dir: Path,
    non_existent_dir: Path,
    base_dir: Path,
) -> Input[PathData]:
    path_value = existing_empty_dir if use_valid_path else non_existent_dir

    return Input(
        data=PathData(
            path=(
                path_value if use_absolute_path else path_value.relative_to(base_dir)
            ),
            base_dir=base_dir,
            use_absolute_path=use_absolute_path,
        ),
        type=InputType.CUSTOM if use_valid_path else InputType.INVALID,
    )


@pytest_cases_parametrize(
    argnames="is_existing_path",
    argvalues=[True, False],
    ids=["existing_path", "non_existent_path"],
)
@pytest_cases_parametrize(
    argnames="use_absolute_path",
    argvalues=[True, False],
    ids=["absolute_path", "relative_path"],
)
def case_repo_dir_data(
    is_existing_path: bool,
    use_absolute_path: bool,
    fixt_crpatcher_existing_empty_dir: Path,
    fixt_crpatcher_non_existent_dir: Path,
    fixt_crpatcher_base_dir: Path,
) -> Input[PathData]:
    return _make_dir_data(
        use_valid_path=is_existing_path,
        use_absolute_path=use_absolute_path,
        existing_empty_dir=fixt_crpatcher_existing_empty_dir,
        non_existent_dir=fixt_crpatcher_non_existent_dir,
        base_dir=fixt_crpatcher_base_dir,
    )


@pytest_cases_parametrize(
    argnames="is_existing_path",
    argvalues=[True, False],
    ids=["existing_path", "non_existent_path"],
)
@pytest_cases_parametrize(
    argnames="use_absolute_path",
    argvalues=[True, False],
    ids=["absolute_path", "relative_path"],
)
def case_patch_dir_data(
    is_existing_path: bool,
    use_absolute_path: bool,
    fixt_crpatcher_existing_empty_dir: Path,
    fixt_crpatcher_non_existent_dir: Path,
    fixt_crpatcher_base_dir: Path,
) -> Input[PathData]:
    return _make_dir_data(
        use_valid_path=is_existing_path,
        use_absolute_path=use_absolute_path,
        existing_empty_dir=fixt_crpatcher_existing_empty_dir,
        non_existent_dir=fixt_crpatcher_non_existent_dir,
        base_dir=fixt_crpatcher_base_dir,
    )


@pytest_cases_parametrize(
    argnames="input",
    argvalues=[
        Input(),  # default
        Input(data=["*.txt", "*.log", "*.py", "*.md"], type=InputType.CUSTOM),
        Input(
            data=["[invalid", "a-format]"], type=InputType.CUSTOM
        ),  # Invalid patterns, but wont raise error. See PatchRequest.ignore_pattern_matcher
    ],
    ids=["default", "valid_patterns", "invalid_patterns_but_wont_raise_error"],
)
def case_ignore_patterns(input: Input[list[str]]):
    return input


@pytest_cases_parametrize(
    argnames="input",
    argvalues=[
        Input(),
        Input(data=["valid_name", "valid_name.txt"], type=InputType.CUSTOM),
        Input(data=["invalid_name/"], type=InputType.INVALID),
    ],
    idgen=Input.idgen_use_input_type(),
)
def case_keep_patch_files(input: Input[list[str]]):
    return input


class CasesProgramContext:
    def case_has_context(self, fixt_crpatcher_existing_empty_file: Path):
        # build validation context from existing file
        return Input(
            data=ProgramContext(config_file=fixt_crpatcher_existing_empty_file),
            type=InputType.CUSTOM,
        )

    def case_no_context(self):
        return Input(data=None, type=InputType.CUSTOM)  # no validation context


@pytest_cases_parametrize_with_cases(
    argnames="program_context",
    cases=CasesProgramContext,
)
@pytest_cases_parametrize_with_cases(
    argnames="repo_dir",
    cases=case_repo_dir_data,
)
@pytest_cases_parametrize_with_cases(
    argnames="patch_dir",
    cases=case_patch_dir_data,
)
@pytest_cases_parametrize_with_cases(
    argnames="ignore_patterns",
    cases=case_ignore_patterns,
)
@pytest_cases_parametrize_with_cases(
    argnames="keep_patch_files",
    cases=case_keep_patch_files,
)
def case_patch_request(
    program_context: Input[ProgramContext | None],
    repo_dir: Input[PathData],
    patch_dir: Input[PathData],
    ignore_patterns: Input[list[str]],
    keep_patch_files: Input[list[str]],
) -> RequestTestInput:
    return RequestTestInput(
        program_context=program_context,
        repo_dir=repo_dir,
        patch_dir=patch_dir,
        ignore_patterns=ignore_patterns,
        keep_patch_files=keep_patch_files,
    )


class TestPatchRequest:
    @pytest_cases_parametrize_with_cases(argnames="test_case", cases=case_patch_request)
    def test_direct_construction(
        self,
        test_case: RequestTestInput,
    ):
        # Test repository config construction behavior.
        # When using absolute paths, direct constructor should work.
        # Otherwise, it should raise ValidationError.

        should_raise_error = not test_case.is_valid

        if not test_case.construction_needs_program_context:
            with (
                pytest.raises(ValidationError) if should_raise_error else nullcontext()
            ):
                other_args: dict[str, Any] = {}
                if test_case.keep_patch_files.type != InputType.DEFAULT:
                    other_args["keep_patch_files"] = (
                        test_case.keep_patch_files.safe_data
                    )
                if test_case.ignore_patterns.type != InputType.DEFAULT:
                    other_args["ignore_patterns"] = test_case.ignore_patterns.safe_data

                config = PatchRequest(
                    repo_dir=test_case.repo_dir.safe_data.path,
                    patch_dir=test_case.patch_dir.safe_data.path,
                    **other_args,
                )

                if not should_raise_error:
                    # Verify paths are absolute and exist
                    assert config.repo_dir.is_absolute()
                    assert config.patch_dir.is_absolute()
                    assert config.repo_dir.is_dir()
                    assert config.patch_dir.is_dir()

                    # Verify paths are resolved correctly.
                    # Since we are using direct construction, the paths must be all absolute and exactly the same as input
                    assert config.repo_dir == test_case.repo_dir.safe_data.path
                    assert config.patch_dir == test_case.patch_dir.safe_data.path

                    if test_case.keep_patch_files.type != InputType.DEFAULT:
                        assert (
                            config.keep_patch_files
                            == test_case.keep_patch_files.safe_data
                        )
                    else:
                        assert config.keep_patch_files == []

                    if test_case.ignore_patterns.type != InputType.DEFAULT:
                        assert (
                            config.ignore_patterns
                            == test_case.ignore_patterns.safe_data
                        )
                    else:
                        assert config.ignore_patterns == []

    @pytest_cases_parametrize_with_cases(argnames="test_case", cases=case_patch_request)
    def test_construction_with_program_context(
        self,
        test_case: RequestTestInput,
    ):
        should_raise_error = not test_case.is_valid

        with pytest.raises(ValidationError) if should_raise_error else nullcontext():
            other_args: dict[str, Any] = {}
            if test_case.keep_patch_files.type != InputType.DEFAULT:
                other_args["keep_patch_files"] = test_case.keep_patch_files.safe_data
            if test_case.ignore_patterns.type != InputType.DEFAULT:
                other_args["ignore_patterns"] = test_case.ignore_patterns.safe_data

            actual_result = PatchRequest.create_with_context(
                program_context=test_case.program_context.safe_data,
                repo_dir=test_case.repo_dir.safe_data.path,
                patch_dir=test_case.patch_dir.safe_data.path,
                **other_args,
            )

            if not should_raise_error:
                # Verify paths are absolute and exist
                assert actual_result.repo_dir.is_absolute()
                assert actual_result.patch_dir.is_absolute()
                assert actual_result.repo_dir.is_dir()
                assert actual_result.patch_dir.is_dir()

                # Verify relative paths are resolved correctly

                expected_repo_dir = (
                    test_case.repo_dir.safe_data.path
                    if test_case.repo_dir.safe_data.use_absolute_path
                    else test_case.repo_dir.safe_data.base_dir.joinpath(
                        test_case.repo_dir.safe_data.path
                    )
                )
                expected_patch_dir = (
                    test_case.patch_dir.safe_data.path
                    if test_case.patch_dir.safe_data.use_absolute_path
                    else test_case.patch_dir.safe_data.base_dir.joinpath(
                        test_case.patch_dir.safe_data.path
                    )
                )

                assert actual_result.repo_dir == expected_repo_dir
                assert actual_result.patch_dir == expected_patch_dir
                assert actual_result.patch_dir == expected_patch_dir

                if test_case.keep_patch_files.type != InputType.DEFAULT:
                    assert (
                        actual_result.keep_patch_files
                        == test_case.keep_patch_files.safe_data
                    )
                else:
                    assert actual_result.keep_patch_files == []

                if test_case.ignore_patterns.type != InputType.DEFAULT:
                    assert (
                        actual_result.ignore_patterns
                        == test_case.ignore_patterns.safe_data
                    )
                else:
                    assert actual_result.ignore_patterns == []
