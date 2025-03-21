# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

from contextlib import nullcontext
from typing import Any, Dict, cast

import pytest
from pydantic import ValidationError
from pytest_cases import case, parametrize, parametrize_with_cases

from crpatcher.config import PatchFileOption
from tests.base.input_data import Input, InputType, NoValue


def _idgen_for_input_str_parametrize(**args: dict[str, Any]) -> str:
    if len(args) != 1:
        raise ValueError(
            "Invalid **args. "
            "This function is only intended to use with @parametrize(`name`, list[Input[str]])."
            f"Actual: {args}"
        )

    name, input_value = next(iter(args.items()))

    if not isinstance(input_value, Input):
        raise ValueError(
            "Invalid value type "
            "This function is only intended to use with @parametrize(`name`, list[Input[str]])."
            f"Actual: {type(input_value)}"
        )

    if not isinstance(input_value.get("data"), str | NoValue):
        raise ValueError(
            "Invalid value type "
            "This function is only intended to use with @parametrize(`name`, list[Input[str]])."
            f"Actual: {input_value}"
        )

    return f"{name}={input_value.type.name.lower()}"


@parametrize(
    "replacement_separator",
    (
        Input[str](),
        Input[str](data="under-score", type=InputType.CUSTOM),
        Input[str](data="invalid+sep", type=InputType.INVALID),
    ),
    idgen=_idgen_for_input_str_parametrize,
)
@parametrize(
    "encoding",
    (
        Input[str](),
        Input[str](data="ascii", type=InputType.CUSTOM),
        Input[str](data="invalid_encoding", type=InputType.INVALID),
    ),
    # idgen=_idgen_for_input_str_parametrize,
)
@parametrize(
    "ext",
    (
        Input[str](),
        Input[str](data="custom_patch", type=InputType.CUSTOM),
        Input[str](data="invalid-ext", type=InputType.INVALID),
    ),
    # idgen=_idgen_for_input_str_parametrize,
)
def test_patch_file_option(
    ext: Input[str],
    encoding: Input[str],
    replacement_separator: Input[str],
) -> None:
    # Determine if any field has invalid value
    should_raise_error = any(
        input_data.is_invalid_data
        for input_data in [ext, encoding, replacement_separator]
    )

    context = pytest.raises(ValidationError) if should_raise_error else nullcontext()

    # Build kwargs dict only including non-DEFAULT fields
    kwargs: Dict[str, Any] = {}
    if ext.type != InputType.DEFAULT:
        kwargs["ext"] = ext.safe_data
    if encoding.type != InputType.DEFAULT:
        kwargs["encoding"] = encoding.safe_data
    if replacement_separator.type != InputType.DEFAULT:
        kwargs["replacement_separator"] = replacement_separator.safe_data

    DEFAULT_VALUES = {
        "ext": "patch",
        "encoding": "utf-8",
        "replacement_separator": "-",
    }

    with context:
        config = PatchFileOption(**kwargs)

        if not should_raise_error:
            # For assertions, compare with value if not DEFAULT, otherwise use PatchFileOption's defaults
            expected_ext = (
                ext.safe_data
                if ext.type != InputType.DEFAULT
                else DEFAULT_VALUES["ext"]
            )
            expected_encoding = (
                encoding.safe_data
                if encoding.type != InputType.DEFAULT
                else DEFAULT_VALUES["encoding"]
            )
            expected_separator = (
                replacement_separator.safe_data
                if replacement_separator.type != InputType.DEFAULT
                else DEFAULT_VALUES["replacement_separator"]
            )

            assert config.ext == expected_ext
            assert config.encoding == expected_encoding
            assert config.replacement_separator == expected_separator
            assert config.replacement_separator == expected_separator
