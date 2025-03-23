# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from pathlib import Path

import pytest

from crpatcher.base.util import (
    calculate_file_checksum_sha256,
    exists_encoding,
    is_filename_only,
)
from tests.base.input_data import Input, InputType
from tests.base.pytest_cases import *


@pytest.fixture(scope="class")
def existing_file_with_content_fixt(crpatcher_base_dir_fixt: Path) -> Path:
    file = crpatcher_base_dir_fixt.joinpath("hello_world.txt").absolute()
    if not file.exists():
        file.touch()
    if not file.is_file():
        raise FileNotFoundError(f"existing_file_with_content_fixt={file} is not a file")
    file.write_text("Hello, world!", encoding="utf-8")
    return file


@pytest_cases_parametrize(
    "path,expected_checksum,type",
    [
        (
            pytest_cases_fixture_ref("crpatcher_existing_empty_file_fixt"),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # hash of empty file
            InputType.CUSTOM,
        ),
        (
            pytest_cases_fixture_ref("crpatcher_non_existent_file_fixt"),
            "",
            InputType.INVALID,
        ),
        (
            pytest_cases_fixture_ref("crpatcher_existing_empty_dir_fixt"),
            "",
            InputType.INVALID,
        ),
        (
            pytest_cases_fixture_ref("existing_file_with_content_fixt"),
            "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3",  # hash of "Hello, world!"
            InputType.CUSTOM,
        ),
    ],
    idgen=lambda **args: f"(type={args['type'].name})-(path={args['path']})",  # type: ignore
)
@pytest_cases_parametrize(
    "buffer_size_input",
    [
        Input[int](),  #  default
        Input(data=1024, type=InputType.CUSTOM),
        Input(data=0, type=InputType.INVALID),  # invalid, must be >= 1
    ],
    idgen=Input.idgen_for_input_parametrize(int),
)
def test_calculate_file_checksum_sha256(
    buffer_size_input: Input[int], path: Path, expected_checksum: str, type: InputType
):
    file_path_input = Input(data=(path, expected_checksum), type=type)

    should_raise_value_error = (
        buffer_size_input.is_invalid_data or file_path_input.is_invalid_data
    )
    with pytest.raises(ValueError) if should_raise_value_error else nullcontext():
        file_path, expected_checksum = file_path_input.safe_data

        result = (
            calculate_file_checksum_sha256(
                file_path=file_path,
                buffer_size=buffer_size_input.safe_data,
            )
            if buffer_size_input.type != InputType.DEFAULT
            else calculate_file_checksum_sha256(file_path=file_path)
        )

        assert result == expected_checksum


def test_exists_encoding():
    assert exists_encoding("utf-8")
    assert not exists_encoding("invalid-encoding")


def test_is_filename_only():
    assert is_filename_only(Path("file.txt"))

    assert not is_filename_only(Path("subdir/file.txt"))

    assert not is_filename_only(Path("/etc/passwd"))

    assert is_filename_only(Path("just_a_name"))
