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
def existing_file_with_content_fixt(fixt_crpatcher_base_dir: Path) -> Path:
    file = fixt_crpatcher_base_dir.joinpath("hello_world.txt").absolute()
    if not file.exists():
        file.touch()
    if not file.is_file():
        raise FileNotFoundError(f"existing_file_with_content_fixt={file} is not a file")
    file.write_text("Hello, world!", encoding="utf-8")
    return file


@pytest_cases_parametrize(
    argnames="path,expected_checksum,type",
    argvalues=[
        (
            pytest_cases_fixture_ref("fixt_crpatcher_existing_empty_file"),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # hash of empty file
            InputType.CUSTOM,
        ),
        (
            pytest_cases_fixture_ref("fixt_crpatcher_non_existent_file"),
            "",
            InputType.INVALID,
        ),
        (
            pytest_cases_fixture_ref("fixt_crpatcher_existing_empty_dir"),
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
    argnames="buffer_size_input",
    argvalues=[
        Input[int](),  #  default
        Input(data=1024, type=InputType.CUSTOM),
        Input(data=0, type=InputType.INVALID),  # invalid, must be >= 1
    ],
    idgen=Input.idgen_use_input_type(),
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
    assert is_filename_only("file.txt")
    assert is_filename_only("my_document")
    assert is_filename_only(".hidden")

    assert not is_filename_only("subdir/file.txt")
    assert not is_filename_only("subdir/")
    assert not is_filename_only("/etc/passwd")
    assert not is_filename_only("report?.doc")  # contains ?
    assert not is_filename_only("CON")  # reserved
    assert not is_filename_only("readme.")  # ends with dot
    assert not is_filename_only("   ")  # just spaces
