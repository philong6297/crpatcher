# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from crpatcher.config import PatchConfig
from tests.base.input_data import InputData, InputType


@pytest.mark.parametrize(
    "ext",
    [
        InputData[str](),
        InputData[str](value="custom_patch", type=InputType.CUSTOM),
        InputData[str](value="invalid-ext", type=InputType.INVALID),
    ],
)
@pytest.mark.parametrize(
    "encoding",
    [
        InputData[str](),
        InputData[str](value="ascii", type=InputType.CUSTOM),
        InputData[str](value="invalid_encoding", type=InputType.INVALID),
    ],
)
@pytest.mark.parametrize(
    "replacement_separator",
    [
        InputData[str](),
        InputData[str](value="under-score", type=InputType.CUSTOM),
        InputData[str](value="invalid+sep", type=InputType.INVALID),
    ],
)
def test_patch_config(
    ext: InputData[str],
    encoding: InputData[str],
    replacement_separator: InputData[str],
) -> None:
    # Determine if any field has invalid value
    should_raise_error = any(
        input_data.should_raise_error
        for input_data in [ext, encoding, replacement_separator]
    )

    context = pytest.raises(ValidationError) if should_raise_error else nullcontext()

    # Build kwargs dict only including non-DEFAULT fields
    kwargs: Dict[str, Any] = {}
    if ext.type != InputType.DEFAULT:
        kwargs["ext"] = ext.value
    if encoding.type != InputType.DEFAULT:
        kwargs["encoding"] = encoding.value
    if replacement_separator.type != InputType.DEFAULT:
        kwargs["replacement_separator"] = replacement_separator.value

    DEFAULT_VALUES = {
        "ext": "patch",
        "encoding": "utf-8",
        "replacement_separator": "-",
    }

    with context:
        config = PatchConfig(**kwargs)

        if not should_raise_error:
            # For assertions, compare with value if not DEFAULT, otherwise use PatchConfig's defaults
            expected_ext = (
                ext.value if ext.type != InputType.DEFAULT else DEFAULT_VALUES["ext"]
            )
            expected_encoding = (
                encoding.value
                if encoding.type != InputType.DEFAULT
                else DEFAULT_VALUES["encoding"]
            )
            expected_separator = (
                replacement_separator.value
                if replacement_separator.type != InputType.DEFAULT
                else DEFAULT_VALUES["replacement_separator"]
            )

            assert config.ext == expected_ext
            assert config.encoding == expected_encoding
            assert config.replacement_separator == expected_separator
