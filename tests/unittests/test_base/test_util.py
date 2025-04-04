# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

import itertools
from contextlib import nullcontext
from pathlib import Path

import pytest

from crpatcher.base.util import (
    calculate_file_checksum_sha256,
    exists_encoding,
    is_file_in_folder,
    is_filename_only,
)
from tests.base.input_data import Input, InputType
from tests.base.pytest_cases import *


@pytest.fixture(scope="class")
def fixt_existing_file_with_content(fixt_crpatcher_base_dir: Path) -> Path:
    file = (fixt_crpatcher_base_dir / "hello_world.txt").absolute()
    if not file.exists():
        file.touch()
    if not file.is_file():
        raise FileNotFoundError(f"fixt_existing_file_with_content={file} is not a file")
    file.write_text("Hello, world!", encoding="utf-8")
    return file


def test_calculate_file_checksum_sha256(
    fixt_crpatcher_existing_empty_file: Path,
    fixt_crpatcher_non_existent_file: Path,
    fixt_crpatcher_existing_empty_dir: Path,
    fixt_existing_file_with_content: Path,
):
    file_path_test_cases = [
        Input(
            data=(
                fixt_crpatcher_existing_empty_file,
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # hash of empty file
            ),
            type=InputType.CUSTOM,
        ),
        Input(
            data=(
                fixt_crpatcher_non_existent_file,
                "",
            ),
            type=InputType.INVALID,
        ),
        Input(
            data=(
                fixt_crpatcher_existing_empty_dir,
                "",
            ),
            type=InputType.INVALID,
        ),
        Input(
            data=(
                fixt_existing_file_with_content,
                "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3",  # hash of "Hello, world!"
            ),
            type=InputType.CUSTOM,
        ),
    ]

    buffer_size_test_cases = [
        Input[int](),  #  default
        Input(data=1024, type=InputType.CUSTOM),
        Input(data=0, type=InputType.INVALID),  # invalid, must be >= 1
    ]

    for file_path_input, buffer_size_input in itertools.product(
        file_path_test_cases, buffer_size_test_cases
    ):
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


def test_is_file_in_folder(
    fixt_crpatcher_existing_empty_dir: Path, fixt_crpatcher_non_existent_dir: Path
):
    folder_path_test_cases = [
        Input(
            data=fixt_crpatcher_existing_empty_dir, type=InputType.CUSTOM
        ),  # valid folder
        Input(
            data=fixt_crpatcher_non_existent_dir, type=InputType.INVALID
        ),  # invalid folder, should raise ValueError
    ]

    valid_file_path = fixt_crpatcher_existing_empty_dir / "valid_file.txt"
    valid_file_path.touch()
    invalid_file_path = fixt_crpatcher_existing_empty_dir / "invalid_file.txt"
    if invalid_file_path.exists():
        invalid_file_path.unlink()

    assert valid_file_path.is_file()
    assert not invalid_file_path.exists()

    file_path_test_cases: list[Input[Path]] = []
    for is_absolute, is_valid_file in itertools.product(
        [True, False],  # is absolute?
        [True, False],  # is valid file?
    ):
        file_path = valid_file_path if is_valid_file else invalid_file_path

        if not is_absolute:
            file_path = file_path.relative_to(fixt_crpatcher_existing_empty_dir)

        file_path_test_cases.append(
            Input(
                data=file_path,
                type=InputType.CUSTOM if is_valid_file else InputType.INVALID,
            )
        )

    for folder_path_input, file_path_input in itertools.product(
        folder_path_test_cases, file_path_test_cases
    ):
        # invalid folder path always raise ValueError regardless of file path
        if folder_path_input.is_invalid_data:
            with pytest.raises(ValueError):
                is_file_in_folder(
                    file_path=file_path_input.safe_data,
                    folder_path=folder_path_input.safe_data,
                )
        else:
            # otherwise, check if file is in folder
            result = is_file_in_folder(
                file_path=file_path_input.safe_data,
                folder_path=folder_path_input.safe_data,
            )
            assert result != file_path_input.is_invalid_data
