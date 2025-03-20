# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from crpatcher.config import PatchInfoConfig
from tests.base.input_data import InputData, InputType


@pytest.mark.parametrize(
    "version",
    [
        InputData[int](),
        InputData[int](value=2, type=InputType.CUSTOM),
        InputData[int](value=0, type=InputType.INVALID),
        InputData[int](value=-1, type=InputType.INVALID),
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
    "ext",
    [
        InputData[str](),
        InputData[str](value="custom_info", type=InputType.CUSTOM),
        InputData[str](value="invalid$ext", type=InputType.INVALID),
    ],
)
def test_patch_info_config(
    version: InputData[int],
    encoding: InputData[str],
    ext: InputData[str],
) -> None:
    # Determine if any field has invalid value
    should_raise_error = any(
        input_data.should_raise_error for input_data in [version, encoding, ext]
    )

    context = pytest.raises(ValidationError) if should_raise_error else nullcontext()

    # Build kwargs dict only including non-DEFAULT fields
    kwargs: Dict[str, Any] = {}
    if version.type != InputType.DEFAULT:
        kwargs["version"] = version.value
    if encoding.type != InputType.DEFAULT:
        kwargs["encoding"] = encoding.value
    if ext.type != InputType.DEFAULT:
        kwargs["ext"] = ext.value

    DEFAULT_VALUES = {
        "version": 1,
        "encoding": "utf-8",
        "ext": "patchinfo",
    }

    with context:
        config = PatchInfoConfig(**kwargs)

        if not should_raise_error:
            # For assertions, compare with value if not DEFAULT, otherwise use PatchInfoConfig's defaults
            expected_version = (
                version.value
                if version.type != InputType.DEFAULT
                else DEFAULT_VALUES["version"]
            )
            expected_encoding = (
                encoding.value
                if encoding.type != InputType.DEFAULT
                else DEFAULT_VALUES["encoding"]
            )
            expected_ext = (
                ext.value if ext.type != InputType.DEFAULT else DEFAULT_VALUES["ext"]
            )

            assert config.version == expected_version
            assert config.encoding == expected_encoding
            assert config.ext == expected_ext
