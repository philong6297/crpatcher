# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

# WARN: this file is only meant to be included by test_crpatcher_config.py
# and should not be used as a standalone file.

from typing import Any, cast

import pytest

from tests.base.input_data import Input, InputType
from tests.unittests.config.helper import *


def _generate_fixt_params_and_ids(fixture_name: str) -> dict[str, Any]:
    pairs = [(type, f"{fixture_name}_{type.name}") for type in InputType]
    params, ids = zip(*pairs)
    return {
        "params": list(params),
        "ids": list(ids),
    }


@pytest.fixture(
    scope="class",
    **_generate_fixt_params_and_ids("requests"),
)
def requests_fixt(
    crpatcher_all_request_test_inputs_fixt: list[RequestTestInput],
    request: pytest.FixtureRequest,
) -> Input[list[RequestTestInput]]:
    if request.param == InputType.DEFAULT:
        return Input()

    valid_requests: list[RequestTestInput] = []
    invalid_requests: list[RequestTestInput] = []

    for data in crpatcher_all_request_test_inputs_fixt:
        if data.is_valid:
            valid_requests.append(data)
        else:
            invalid_requests.append(data)

    if request.param == InputType.CUSTOM:
        return Input(
            data=valid_requests,
            type=InputType.CUSTOM,
        )

    return Input(
        data=invalid_requests,
        type=InputType.INVALID,
    )


@pytest.fixture(
    scope="class",
    **_generate_fixt_params_and_ids("patch_file_opt"),
)
def patch_file_opt_fixt(
    request: pytest.FixtureRequest,
) -> Input[PatchFileOptionTestInput]:
    match cast(InputType, request.param):
        case InputType.DEFAULT:
            return Input()
        case InputType.CUSTOM:
            return Input(
                data=PatchFileOptionTestInput(
                    ext="custom_ext",
                    encoding="ascii",
                    replacement_separator="custom-replacement-separator",
                ),
                type=InputType.CUSTOM,
            )
        case InputType.INVALID:
            return Input(
                data=PatchFileOptionTestInput(
                    ext="invalid-ext",
                    encoding="invalid-encoding",
                    replacement_separator="invalid+sep",
                ),
                type=InputType.INVALID,
            )


@pytest.fixture(
    scope="class",
    **_generate_fixt_params_and_ids("patchinfo_file_opt"),
)
def patchinfo_file_opt_fixt(
    request: pytest.FixtureRequest,
) -> Input[PatchInfoOptionTestInput]:
    match cast(InputType, request.param):
        case InputType.DEFAULT:
            return Input()
        case InputType.CUSTOM:
            return Input(
                data=PatchInfoOptionTestInput(
                    version=2,
                    ext="custom_ext",
                    encoding="ascii",
                ),
                type=InputType.CUSTOM,
            )
        case InputType.INVALID:
            return Input(
                data=PatchInfoOptionTestInput(
                    version=-1,
                    ext="invalid$ext",
                    encoding="invalid_encoding",
                ),
                type=InputType.INVALID,
            )
