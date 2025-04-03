# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import itertools
import json
import uuid
from contextlib import nullcontext
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from crpatcher.config import CrPatcherConfig, PatchFileOption
from tests.base.input_data import Input, InputType
from tests.base.pytest_cases import (
    pytest_cases_fixture,
    pytest_cases_fixture_ref,
    pytest_cases_parametrize,
)
from tests.unittests.test_config.helper import (
    PatchFileOptionTestInput,
    RequestTestInput,
)
from tests.unittests.test_config.tc_builder import (
    PATCH_FILE_OPTION_TEST_CASE_BUILDER,
    PATCH_REQUEST_TEST_CASE_BUILDER,
)

RequestTestCase = Input[list[RequestTestInput]]
PatchFileOptionTestCase = PatchFileOptionTestInput
CrPatcherTestCase = tuple[RequestTestCase, PatchFileOptionTestCase]


@pytest_cases_fixture(scope="function")
def fixt_all_test_cases(
    fixt_crpatcher_existing_empty_file: Path,
    fixt_crpatcher_existing_empty_dir: Path,
    fixt_crpatcher_non_existent_dir: Path,
    fixt_crpatcher_base_dir: Path,
) -> list[CrPatcherTestCase]:
    all_requests = PATCH_REQUEST_TEST_CASE_BUILDER.build_all_requests(
        existing_empty_file=fixt_crpatcher_existing_empty_file,
        existing_empty_dir=fixt_crpatcher_existing_empty_dir,
        non_existent_dir=fixt_crpatcher_non_existent_dir,
        base_dir=fixt_crpatcher_base_dir,
    )

    valid: list[RequestTestInput] = []
    invalid: list[RequestTestInput] = []

    for request in all_requests:
        if request.is_valid:
            valid.append(request)
        else:
            invalid.append(request)

    requests_test_cases: list[RequestTestCase] = [
        Input(),  # default
        Input(data=valid, type=InputType.CUSTOM),
        Input(data=invalid, type=InputType.INVALID),
    ]

    patch_file_option_test_cases: list[PatchFileOptionTestCase] = [
        PATCH_FILE_OPTION_TEST_CASE_BUILDER.build_patch_file_option_test_input(
            extension_arg=extension_arg,
            name_separator_arg=name_separator_arg,
            encoding_arg=encoding_arg,
        )
        for extension_arg, name_separator_arg, encoding_arg in itertools.product(
            PATCH_FILE_OPTION_TEST_CASE_BUILDER.EXTENSION_CONSTRUCTION_TEST_CASES,
            PATCH_FILE_OPTION_TEST_CASE_BUILDER.NAME_SEPARATOR_CONSTRUCTION_TEST_CASES,
            PATCH_FILE_OPTION_TEST_CASE_BUILDER.ENCODING_CONSTRUCTION_TEST_CASES,
        )
    ]

    return list(
        itertools.product(
            requests_test_cases,
            patch_file_option_test_cases,
        )
    )


def test_direct_construction(fixt_all_test_cases: list[CrPatcherTestCase]) -> None:
    # Direct construction can only be tested with valid input data. Since any invalid input should raise error from the construction of each field member itself.
    for requests_arg, patch_file_option_arg in fixt_all_test_cases:
        if (
            requests_arg.type == InputType.INVALID
            or patch_file_option_arg.get_input_type == InputType.INVALID
        ):
            return

        expected: dict[str, Any] = {
            "requests": [],
            "patch_file_option": PatchFileOption(),
        }

        # Build kwargs dict only including non-DEFAULT fields
        kwargs: dict[str, Any] = {}

        if requests_arg.type != InputType.DEFAULT:
            expected["requests"] = [
                request.build_patch_request() for request in requests_arg.safe_data
            ]

            kwargs["requests"] = expected["requests"]

        if patch_file_option_arg.get_input_type != InputType.DEFAULT:
            expected["patch_file_option"] = (
                patch_file_option_arg.build_patch_file_option()
            )
            kwargs["patch_file_option"] = expected["patch_file_option"]

        actual_config = CrPatcherConfig(**kwargs)

        assert actual_config.requests == expected["requests"]
        assert actual_config.patch_file_option == expected["patch_file_option"]


@pytest_cases_parametrize(
    argnames="config_file",
    argvalues=[
        pytest_cases_fixture_ref("fixt_crpatcher_non_existent_file"),  # not exist
        pytest_cases_fixture_ref("fixt_crpatcher_existing_empty_dir"),  # not a file
        pytest_cases_fixture_ref(
            "fixt_crpatcher_existing_empty_file"
        ),  # not a valid json format
    ],
    ids=[
        "not_exist",
        "not_a_file",
        "not_a_valid_json",
    ],
)
def test_create_from_invalid_config_file(config_file: Path) -> None:
    with pytest.raises(ValidationError):
        CrPatcherConfig.create_from_config_file(config_file)


def test_create_from_existing_config_file(
    fixt_crpatcher_base_dir: Path, fixt_all_test_cases: list[CrPatcherTestCase]
) -> None:
    for requests_arg, patch_file_option_arg in fixt_all_test_cases:
        valid_config_file = _create_config_file(
            base_dir=fixt_crpatcher_base_dir,
            requests=requests_arg,
            patch_file_option=patch_file_option_arg,
        )

        should_raise_error = (
            requests_arg.is_invalid_data
            or patch_file_option_arg.get_input_type == InputType.INVALID
        )

        with pytest.raises(ValidationError) if should_raise_error else nullcontext():
            actual_config = CrPatcherConfig.create_from_config_file(valid_config_file)

            if not should_raise_error:
                expected_requests = (
                    [
                        request.build_patch_request()
                        for request in requests_arg.safe_data
                    ]
                    if requests_arg.type == InputType.CUSTOM
                    else []
                )

                expected_patch_file_option = (
                    patch_file_option_arg.build_patch_file_option()
                    if patch_file_option_arg.get_input_type == InputType.CUSTOM
                    else PatchFileOption()
                )

                assert actual_config.requests == expected_requests
                assert actual_config.patch_file_option == expected_patch_file_option


def _create_config_file(
    *,
    base_dir: Path,
    requests: Input[list[RequestTestInput]],
    patch_file_option: PatchFileOptionTestInput,
) -> Path:
    filename = f"{uuid.uuid4()}.json"
    config_file = base_dir / filename

    if config_file.exists():
        raise FileExistsError(
            f"Config file {config_file.as_posix()} already exists. It should be not at the time of running this test"
        )

    data: dict[str, Any] = {}

    if patch_file_option.get_input_type != InputType.DEFAULT:
        # manually build the dict because we has invalid input data, which cannot just use PatchFileOptionTestInput.build_patch_file_option()
        patch_file_option_raw: dict[str, Any] = {}
        if patch_file_option.extension.type != InputType.DEFAULT:
            patch_file_option_raw["extension"] = patch_file_option.extension.safe_data
        if patch_file_option.name_separator.type != InputType.DEFAULT:
            patch_file_option_raw["name_separator"] = (
                patch_file_option.name_separator.safe_data
            )
        if patch_file_option.encoding.type != InputType.DEFAULT:
            patch_file_option_raw["encoding"] = patch_file_option.encoding.safe_data

        data["patch_file_option"] = patch_file_option_raw

    if requests.type != InputType.DEFAULT:
        requests_raw: list[dict[str, Any]] = []
        for request in requests.safe_data:
            other_args: dict[str, Any] = {}
            if request.keep_patch_files.type != InputType.DEFAULT:
                other_args["keep_patch_files"] = request.keep_patch_files.safe_data
            if request.ignore_patterns.type != InputType.DEFAULT:
                other_args["ignore_patterns"] = request.ignore_patterns.safe_data
            # program_context is based on the config file itself, we dont need to serialize it

            requests_raw.append(
                {
                    # PatchRequest contains pathlib.Path, which is not serializable by default
                    "repo_dir": request.repo_dir.safe_data.path.as_posix(),
                    "patch_dir": request.patch_dir.safe_data.path.as_posix(),
                    **other_args,
                }
            )

        data["requests"] = requests_raw

    with open(config_file, "w") as f:
        json.dump(data, f)

    return config_file
