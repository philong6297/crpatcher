# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

import contextlib
from typing import Any

import pytest
from pydantic import ValidationError

from crpatcher.config import PatchFileOption
from tests.base.input_data import Input, InputType
from tests.base.pytest_cases import pytest_cases_parametrize
from tests.unittests.test_config.test_case_builder import (
    PATCH_FILE_OPTION_TEST_CASE_BUILDER,
)


def _idgen_for_fixt_patch_file_option(**kwargs: dict[str, Any]) -> str:
    extension_id = kwargs["extension_id"]
    name_separator_id = kwargs["name_separator_id"]
    encoding_id = kwargs["encoding_id"]

    return (
        f"(extension=({extension_id}))-"
        f"(name_separator=({name_separator_id}))-"
        f"(encoding=({encoding_id}))"
    )


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
def test_direct_constructor(
    extension_arg: Input[str],
    name_separator_arg: Input[str],
    encoding_arg: Input[str],
    extension_id: str,  # unused
    name_separator_id: str,  # unused
    encoding_id: str,  # unused
):
    should_raise_error = (
        extension_arg.is_invalid_data
        or name_separator_arg.is_invalid_data
        or encoding_arg.is_invalid_data
    )

    with (
        pytest.raises(ValidationError)
        if should_raise_error
        else contextlib.nullcontext()
    ):
        kwargs: dict[str, Any] = {}

        # default values
        expected = {
            "extension": "patch",
            "name_separator": "-",
            "encoding": "utf-8",
        }

        # mimic default value by adding to kwargs first. only set the value if the input is custom

        if extension_arg.type != InputType.DEFAULT:
            expected["extension"] = extension_arg.safe_data
            kwargs["extension"] = expected["extension"]
        if name_separator_arg.type != InputType.DEFAULT:
            expected["name_separator"] = name_separator_arg.safe_data
            kwargs["name_separator"] = expected["name_separator"]
        if encoding_arg.type != InputType.DEFAULT:
            expected["encoding"] = encoding_arg.safe_data
            kwargs["encoding"] = expected["encoding"]

        actual = PatchFileOption(**kwargs)

        if not should_raise_error:
            assert actual.extension == expected["extension"]
            assert actual.name_separator == expected["name_separator"]
            assert actual.encoding == expected["encoding"]
            assert actual.name_separator == expected["name_separator"]
            assert actual.encoding == expected["encoding"]
