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
from tests.unittests.test_config.arg_builder import PATCH_FILE_OPTION_ARG_BUILDER


@pytest_cases_parametrize(
    argnames="extension",
    argvalues=PATCH_FILE_OPTION_ARG_BUILDER.EXTENSION_ARGVALUES,
    ids=[f"(extension={id})" for id in PATCH_FILE_OPTION_ARG_BUILDER.EXTENSION_IDS],
)
@pytest_cases_parametrize(
    argnames="name_separator",
    argvalues=PATCH_FILE_OPTION_ARG_BUILDER.NAME_SEPARATOR_ARGVALUES,
    ids=[
        f"(name_separator={id})"
        for id in PATCH_FILE_OPTION_ARG_BUILDER.NAME_SEPARATOR_IDS
    ],
)
@pytest_cases_parametrize(
    argnames="encoding",
    argvalues=PATCH_FILE_OPTION_ARG_BUILDER.ENCODING_ARGVALUES,
    ids=[f"(encoding={id})" for id in PATCH_FILE_OPTION_ARG_BUILDER.ENCODING_IDS],
)
def test_direct_constructor(
    extension: Input[str], name_separator: Input[str], encoding: Input[str]
):
    should_raise_error = (
        extension.is_invalid_data
        or name_separator.is_invalid_data
        or encoding.is_invalid_data
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

        if extension.type != InputType.DEFAULT:
            expected["extension"] = extension.safe_data
            kwargs["extension"] = expected["extension"]
        if name_separator.type != InputType.DEFAULT:
            expected["name_separator"] = name_separator.safe_data
            kwargs["name_separator"] = expected["name_separator"]
        if encoding.type != InputType.DEFAULT:
            expected["encoding"] = encoding.safe_data
            kwargs["encoding"] = expected["encoding"]

        actual = PatchFileOption(**kwargs)

        if not should_raise_error:
            assert actual.extension == expected["extension"]
            assert actual.name_separator == expected["name_separator"]
            assert actual.encoding == expected["encoding"]
