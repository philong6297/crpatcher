# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import json
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
    pytest_cases_parametrize_with_cases,
)
from tests.unittests.test_config.helper import (
    PatchFileOptionTestInput,
    RequestTestInput,
)
from tests.unittests.test_config.test_case_builder import (
    PATCH_FILE_OPTION_TEST_CASE_BUILDER,
    PATCH_REQUEST_TEST_CASE_BUILDER,
)


@pytest_cases_fixture(scope="class")
@pytest_cases_parametrize(
    argnames="input_type",
    argvalues=list(InputType),
    ids=[f"(requests={type.name})" for type in InputType],
)
def fixt_requests(
    input_type: InputType,
    fixt_crpatcher_existing_empty_file: Path,
    fixt_crpatcher_existing_empty_dir: Path,
    fixt_crpatcher_non_existent_dir: Path,
    fixt_crpatcher_base_dir: Path,
) -> Input[list[RequestTestInput]]:
    if input_type == InputType.DEFAULT:
        return Input()

    all_requests = PATCH_REQUEST_TEST_CASE_BUILDER.build_all_requests(
        existing_empty_file=fixt_crpatcher_existing_empty_file,
        existing_empty_dir=fixt_crpatcher_existing_empty_dir,
        non_existent_dir=fixt_crpatcher_non_existent_dir,
        base_dir=fixt_crpatcher_base_dir,
    )

    valid_requests: list[RequestTestInput] = []
    invalid_requests: list[RequestTestInput] = []

    for data in all_requests:
        if data.is_valid:
            valid_requests.append(data)
        else:
            invalid_requests.append(data)

    if input_type == InputType.CUSTOM:
        return Input(
            data=valid_requests,
            type=InputType.CUSTOM,
        )
    elif input_type == InputType.INVALID:
        return Input(
            data=invalid_requests,
            type=InputType.INVALID,
        )
    else:
        raise ValueError("Not reachable")


def _idgen_for_fixt_patch_file_option(**kwargs: dict[str, Any]) -> str:
    extension_id = kwargs["extension_id"]
    name_separator_id = kwargs["name_separator_id"]
    encoding_id = kwargs["encoding_id"]

    data_str = (
        f"(extension=({extension_id}))-"
        f"(name_separator=({name_separator_id}))-"
        f"(encoding=({encoding_id}))"
    )

    return f"(requests={data_str})"


@pytest_cases_fixture(scope="class")
@pytest_cases_parametrize(
    idgen=_idgen_for_fixt_patch_file_option,
    **{
        "extension_arg,extension_id": list(
            zip(
                PATCH_FILE_OPTION_TEST_CASE_BUILDER.EXTENSION_CONSTRUCTION_TEST_CASES,
                PATCH_FILE_OPTION_TEST_CASE_BUILDER.EXTENSION_CONSTRUCTION_TEST_CASE_IDS,
            )
        ),
        "name_separator_arg,name_separator_id": list(
            zip(
                PATCH_FILE_OPTION_TEST_CASE_BUILDER.NAME_SEPARATOR_CONSTRUCTION_TEST_CASES,
                PATCH_FILE_OPTION_TEST_CASE_BUILDER.NAME_SEPARATOR_CONSTRUCTION_TEST_CASE_IDS,
            )
        ),
        "encoding_arg,encoding_id": list(
            zip(
                PATCH_FILE_OPTION_TEST_CASE_BUILDER.ENCODING_CONSTRUCTION_TEST_CASES,
                PATCH_FILE_OPTION_TEST_CASE_BUILDER.ENCODING_CONSTRUCTION_TEST_CASE_IDS,
            )
        ),
    },
)
def fixt_patch_file_option(
    extension_arg: Input[str],
    name_separator_arg: Input[str],
    encoding_arg: Input[str],
    extension_id: str,  # unused
    name_separator_id: str,  # unused
    encoding_id: str,  # unused
) -> PatchFileOptionTestInput:
    return PATCH_FILE_OPTION_TEST_CASE_BUILDER.build_patch_file_option_test_input(
        extension_arg=extension_arg,
        name_separator_arg=name_separator_arg,
        encoding_arg=encoding_arg,
    )


def test_direct_construction(
    fixt_requests: Input[list[RequestTestInput]],
    fixt_patch_file_option: PatchFileOptionTestInput,
) -> None:
    # Direct construction can only be tested with valid input data. Since any invalid input should raise error from the construction of each field member itself.
    if (
        fixt_requests.type == InputType.INVALID
        or fixt_patch_file_option.get_input_type == InputType.INVALID
    ):
        return

    expected: dict[str, Any] = {
        "requests": [],
        "patch_file_option": PatchFileOption(),
    }

    # Build kwargs dict only including non-DEFAULT fields
    kwargs: dict[str, Any] = {}

    if fixt_requests.type != InputType.DEFAULT:
        expected["requests"] = [
            request.build_patch_request() for request in fixt_requests.safe_data
        ]

        kwargs["requests"] = expected["requests"]

    if fixt_patch_file_option.get_input_type != InputType.DEFAULT:
        expected["patch_file_option"] = fixt_patch_file_option.build_patch_file_option()
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
    fixt_crpatcher_base_dir: Path,
    fixt_requests: Input[list[RequestTestInput]],
    fixt_patch_file_option: PatchFileOptionTestInput,
) -> None:
    valid_config_file = _create_config_file(
        base_dir=fixt_crpatcher_base_dir,
        requests=fixt_requests,
        patch_file_option=fixt_patch_file_option,
    )

    should_raise_error = (
        fixt_requests.is_invalid_data
        or fixt_patch_file_option.get_input_type == InputType.INVALID
    )

    with pytest.raises(ValidationError) if should_raise_error else nullcontext():
        actual_config = CrPatcherConfig.create_from_config_file(valid_config_file)

        if not should_raise_error:
            expected_requests = (
                [request.build_patch_request() for request in fixt_requests.safe_data]
                if fixt_requests.type == InputType.CUSTOM
                else []
            )

            expected_patch_file_option = (
                fixt_patch_file_option.build_patch_file_option()
                if fixt_patch_file_option.get_input_type == InputType.CUSTOM
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
    filename = (
        f"requests_{requests.type.name}_"
        f"patch_file_option_{patch_file_option.get_input_type.name}"
        ".json"
    )
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
    return config_file
    return config_file
    return config_file
