# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from typing import Any, Dict, get_type_hints

import pytest
from pydantic import ValidationError

from crpatcher.config import PatchInfoConfig
from tests.base.input_data import InputData, InputType

# Get field types from PatchInfoConfig
patch_info_config_types = get_type_hints(PatchInfoConfig)


@pytest.mark.parametrize(
    "version",
    [
        InputData(),
        InputData(value=2, type=InputType.CUSTOM),
        InputData(value=0, type=InputType.INVALID),
        InputData(value=-1, type=InputType.INVALID),
        InputData(value=float("inf"), type=InputType.INVALID),
        InputData(value=float("nan"), type=InputType.INVALID),
        InputData(value="invalid-version", type=InputType.INVALID),
        InputData(value=0.1, type=InputType.INVALID),
    ],
)
@pytest.mark.parametrize(
    "encoding",
    [
        InputData(),
        InputData(value="ascii", type=InputType.CUSTOM),
        InputData(value="invalid_encoding", type=InputType.INVALID),
    ],
)
@pytest.mark.parametrize(
    "ext",
    [
        InputData(),
        InputData(value="custom_info", type=InputType.CUSTOM),
        InputData(value="invalid$ext", type=InputType.INVALID),
    ],
)
def test_patch_info_config(
    version: InputData,
    encoding: InputData,
    ext: InputData,
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
