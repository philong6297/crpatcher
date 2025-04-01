# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from crpatcher.config import PatchRequest
from tests.base.input_data import Input, InputType
from tests.base.pytest_cases import pytest_cases_fixture, pytest_cases_parametrize
from tests.unittests.test_config.helper import RequestTestInput
from tests.unittests.test_config.test_case_builder import (
    PATCH_REQUEST_TEST_CASE_BUILDER,
)


def _idgen_for_fixt_patch_request(**kwargs: dict[str, Any]) -> str:
    print(kwargs)
    repo_dir_id = kwargs["repo_dir_id"]
    patch_dir_id = kwargs["patch_dir_id"]
    ignore_patterns_id = kwargs["ignore_patterns_id"]
    keep_patch_files_id = kwargs["keep_patch_files_id"]
    program_context_id = kwargs["program_context_id"]

    return (
        f"(repo_dir=({repo_dir_id}))-"
        f"(patch_dir=({patch_dir_id}))-"
        f"(ignore_patterns=({ignore_patterns_id}))-"
        f"(keep_patch_files=({keep_patch_files_id}))-"
        f"(program_context=({program_context_id}))"
    )


@pytest_cases_fixture(scope="class")
@pytest_cases_parametrize(
    idgen=_idgen_for_fixt_patch_request,
    **{
        "repo_dir_arg,repo_dir_id": list(
            zip(
                PATCH_REQUEST_TEST_CASE_BUILDER.REPO_DIR_CONSTRUCTION_TEST_CASES,
                PATCH_REQUEST_TEST_CASE_BUILDER.REPO_DIR_CONSTRUCTION_TEST_CASE_IDS,
            )
        ),
        "patch_dir_arg,patch_dir_id": list(
            zip(
                PATCH_REQUEST_TEST_CASE_BUILDER.PATCH_DIR_CONSTRUCTION_TEST_CASES,
                PATCH_REQUEST_TEST_CASE_BUILDER.PATCH_DIR_CONSTRUCTION_TEST_CASE_IDS,
            )
        ),
        "ignore_patterns_arg,ignore_patterns_id": list(
            zip(
                PATCH_REQUEST_TEST_CASE_BUILDER.IGNORE_PATTERNS_CONSTRUCTION_TEST_CASES,
                PATCH_REQUEST_TEST_CASE_BUILDER.IGNORE_PATTERNS_CONSTRUCTION_TEST_CASE_IDS,
            )
        ),
        "keep_patch_files_arg,keep_patch_files_id": list(
            zip(
                PATCH_REQUEST_TEST_CASE_BUILDER.KEEP_PATCH_FILES_CONSTRUCTION_TEST_CASES,
                PATCH_REQUEST_TEST_CASE_BUILDER.KEEP_PATCH_FILES_CONSTRUCTION_TEST_CASE_IDS,
            )
        ),
        "program_context_arg,program_context_id": list(
            zip(
                PATCH_REQUEST_TEST_CASE_BUILDER.PROGRAM_CONTEXT_CONSTRUCTION_TEST_CASES,
                PATCH_REQUEST_TEST_CASE_BUILDER.PROGRAM_CONTEXT_CONSTRUCTION_TEST_CASE_IDS,
            )
        ),
    },
)
def fixt_patch_request(
    repo_dir_arg: tuple[bool, bool],
    patch_dir_arg: tuple[bool, bool],
    ignore_patterns_arg: Input[list[str]],
    keep_patch_files_arg: Input[list[str]],
    program_context_arg: bool,
    fixt_crpatcher_existing_empty_file: Path,
    fixt_crpatcher_existing_empty_dir: Path,
    fixt_crpatcher_non_existent_dir: Path,
    fixt_crpatcher_base_dir: Path,
    repo_dir_id: str,  # unused
    patch_dir_id: str,  # unused
    ignore_patterns_id: str,  # unused
    keep_patch_files_id: str,  # unused
    program_context_id: str,  # unused
) -> RequestTestInput:
    return PATCH_REQUEST_TEST_CASE_BUILDER.build_request_test_input(
        repo_dir_arg=repo_dir_arg,
        patch_dir_arg=patch_dir_arg,
        ignore_patterns_arg=ignore_patterns_arg,
        keep_patch_files_arg=keep_patch_files_arg,
        program_context_arg=program_context_arg,
        existing_empty_file=fixt_crpatcher_existing_empty_file,
        existing_empty_dir=fixt_crpatcher_existing_empty_dir,
        non_existent_dir=fixt_crpatcher_non_existent_dir,
        base_dir=fixt_crpatcher_base_dir,
    )


def test_direct_construction(
    fixt_patch_request: RequestTestInput,
):
    # Test repository config construction behavior.
    # When using absolute paths, direct constructor should work.
    # Otherwise, it should raise ValidationError.

    test_case = fixt_patch_request

    should_raise_error = not test_case.is_valid

    if not test_case.construction_needs_program_context:
        with pytest.raises(ValidationError) if should_raise_error else nullcontext():
            other_args: dict[str, Any] = {}
            if test_case.keep_patch_files.type != InputType.DEFAULT:
                other_args["keep_patch_files"] = test_case.keep_patch_files.safe_data
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
                        config.keep_patch_files == test_case.keep_patch_files.safe_data
                    )
                else:
                    assert config.keep_patch_files == []

                if test_case.ignore_patterns.type != InputType.DEFAULT:
                    assert config.ignore_patterns == test_case.ignore_patterns.safe_data
                else:
                    assert config.ignore_patterns == []


def test_construction_with_program_context(
    fixt_patch_request: RequestTestInput,
):
    test_case = fixt_patch_request

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
                else test_case.repo_dir.safe_data.base_dir
                / test_case.repo_dir.safe_data.path
            )
            expected_patch_dir = (
                test_case.patch_dir.safe_data.path
                if test_case.patch_dir.safe_data.use_absolute_path
                else test_case.patch_dir.safe_data.base_dir
                / test_case.patch_dir.safe_data.path
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
                    actual_result.ignore_patterns == test_case.ignore_patterns.safe_data
                )
            else:
                assert actual_result.ignore_patterns == []
