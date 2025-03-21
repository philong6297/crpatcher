# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from crpatcher.config import PatchInfoOption
from tests.base.input_data import Input, InputType


@pytest.mark.parametrize(
    "version",
    [
        Input[int](),
        Input[int](data=2, type=InputType.CUSTOM),
        Input[int](data=0, type=InputType.INVALID),
        Input[int](data=-1, type=InputType.INVALID),
    ],
)
@pytest.mark.parametrize(
    "encoding",
    [
        Input[str](),
        Input[str](data="ascii", type=InputType.CUSTOM),
        Input[str](data="invalid_encoding", type=InputType.INVALID),
    ],
)
@pytest.mark.parametrize(
    "ext",
    [
        Input[str](),
        Input[str](data="custom_info", type=InputType.CUSTOM),
        Input[str](data="invalid$ext", type=InputType.INVALID),
    ],
)
def test_patchinfo_file_option(
    version: Input[int],
    encoding: Input[str],
    ext: Input[str],
) -> None:
    # Determine if any field has invalid value
    should_raise_error = any(
        input_data.is_invalid_data for input_data in [version, encoding, ext]
    )

    context = pytest.raises(ValidationError) if should_raise_error else nullcontext()

    # Build kwargs dict only including non-DEFAULT fields
    kwargs: Dict[str, Any] = {}
    if version.type != InputType.DEFAULT:
        kwargs["version"] = version.safe_data
    if encoding.type != InputType.DEFAULT:
        kwargs["encoding"] = encoding.safe_data
    if ext.type != InputType.DEFAULT:
        kwargs["ext"] = ext.safe_data

    DEFAULT_VALUES = {
        "version": 1,
        "encoding": "utf-8",
        "ext": "patchinfo",
    }

    with context:
        config = PatchInfoOption(**kwargs)

        if not should_raise_error:
            # For assertions, compare with value if not DEFAULT, otherwise use PatchInfoOption's defaults
            expected_version = (
                version.safe_data
                if version.type != InputType.DEFAULT
                else DEFAULT_VALUES["version"]
            )
            expected_encoding = (
                encoding.safe_data
                if encoding.type != InputType.DEFAULT
                else DEFAULT_VALUES["encoding"]
            )
            expected_ext = (
                ext.safe_data
                if ext.type != InputType.DEFAULT
                else DEFAULT_VALUES["ext"]
            )

            assert config.version == expected_version
            assert config.encoding == expected_encoding
            assert config.ext == expected_ext
