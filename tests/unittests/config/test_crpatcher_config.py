# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, cast

import pytest

from crpatcher.config import (
    CRPatcherConfig,
    PatchConfig,
    PatchInfoConfig,
    RepositoryConfig,
)
from tests.base.input_data import InputData, InputType
from tests.unittests.config._test_crpatcher_config_inc import *


@pytest.mark.usefixtures(
    "patch_config_fixt", "patch_info_config_fixt", "repositories_fixt"
)
class TestCRPatcherConfig:
    def test_crpatcher_config(
        self,
        patch_config_fixt: InputData[PatchConfigTestData],
        patch_info_config_fixt: InputData[PatchInfoConfigTestData],
        repositories_fixt: InputData[list[RepositoryTestData]],
    ) -> None:
        self._test_direct_construction(
            patch_config_fixt, patch_info_config_fixt, repositories_fixt
        )

    def _test_direct_construction(
        self,
        patch_config_fixt: InputData[PatchConfigTestData],
        patch_info_config_fixt: InputData[PatchInfoConfigTestData],
        repositories_fixt: InputData[list[RepositoryTestData]],
    ) -> None:
        # Direct construction can only be tested with valid input data. Since any invalid input should raise error from the construction of each field member itself.
        if (
            patch_config_fixt.type == InputType.INVALID
            or patch_info_config_fixt.type == InputType.INVALID
            or repositories_fixt.type == InputType.INVALID
        ):
            return

        # Build kwargs dict only including non-DEFAULT fields
        kwargs: Dict[str, Any] = {}

        expected_config = CRPATCHER_CONFIG_DEFAULT_VALUES

        # if (
        #     patch_config_fixt.type == InputType.CUSTOM
        #     and patch_info_config_fixt.type == InputType.DEFAULT
        #     and repositories_fixt.type == InputType.CUSTOM
        # ):
        #     pass

        if patch_config_fixt.type != InputType.DEFAULT:
            expected_config["patch_config"] = (
                patch_config_fixt.safe_value.build_patch_config()
            )

            kwargs["patch_config"] = expected_config["patch_config"]

        if patch_info_config_fixt.type != InputType.DEFAULT:
            expected_config["patch_info_config"] = (
                patch_info_config_fixt.safe_value.build_patch_info_config()
            )
            kwargs["patch_info_config"] = expected_config["patch_info_config"]

        if repositories_fixt.type != InputType.DEFAULT:
            expected_config["repositories"] = [
                repository_data.build_repository_config()
                for repository_data in repositories_fixt.safe_value
            ]
            kwargs["repositories"] = expected_config["repositories"]

        result = CRPatcherConfig(**kwargs)

        # For assertions, compare with value if not DEFAULT, otherwise use defaults
        assert result.patch_config == expected_config["patch_config"]
        assert result.patch_info_config == expected_config["patch_info_config"]
        assert result.repositories == expected_config["repositories"]

    def _test_create_from_config_file_valid(
        self,
        crpatcher_test_base_dir: Path,
        patch_config_fixt: InputData,
        patch_info_config_fixt: InputData,
        valid_repositories_fixt: InputData,
    ) -> None:
        valid_config_file = _create_valid_config_file(
            crpatcher_test_base_dir,
            patch_config_fixt,
            patch_info_config_fixt,
            valid_repositories_fixt,
        )

        config = CRPatcherConfig.create_from_config_file(valid_config_file)

        assert config.patch_config == (
            patch_config_fixt.value
            if patch_config_fixt.type != InputType.DEFAULT
            else CRPATCHER_CONFIG_DEFAULT_VALUES["patch_config"]
        )

        assert config.patch_info_config == (
            patch_info_config_fixt.value
            if patch_info_config_fixt.type != InputType.DEFAULT
            else CRPATCHER_CONFIG_DEFAULT_VALUES["patch_info_config"]
        )

        assert config.repositories == (
            valid_repositories_fixt.value
            if valid_repositories_fixt.type != InputType.DEFAULT
            else CRPATCHER_CONFIG_DEFAULT_VALUES["repositories"]
        )


def _create_valid_config_file(
    crpatcher_test_base_dir: Path,
    patch_config_fixt: InputData,
    patch_info_config_fixt: InputData,
    valid_repositories_fixt: InputData,
) -> Path:
    # Construct the file name based on fixture states
    patch_config_name = f"patch_config_{'default' if patch_config_fixt.type == InputType.DEFAULT else 'custom'}"
    patch_info_config_name = f"patch_info_config_{'default' if patch_info_config_fixt.type == InputType.DEFAULT else 'custom'}"
    repositories_name = f"repositories_{'default' if valid_repositories_fixt.type == InputType.DEFAULT else 'custom'}"
    config_file_name = f"valid_config_{patch_config_name}_{patch_info_config_name}_{repositories_name}.yaml"
    # Define the path for the config file
    config_file = crpatcher_test_base_dir.joinpath(config_file_name)

    if config_file.is_file():
        raise FileExistsError(
            f"Config file {config_file.as_posix()} already exists. It should be not at the time of running this test"
        )

    data: dict[str, Any] = {}

    if patch_config_fixt.type != InputType.DEFAULT:
        data["patch_config"] = cast(PatchConfig, patch_config_fixt.value).model_dump()

    if patch_info_config_fixt.type != InputType.DEFAULT:
        data["patch_info_config"] = cast(
            PatchInfoConfig, patch_info_config_fixt.value
        ).model_dump()

    if valid_repositories_fixt.type != InputType.DEFAULT:
        data["repositories"] = [
            # RepositoryConfig contains pathlib.Path, which is not serializable by default
            # need to load as json
            json.loads(repo.model_dump_json())
            for repo in cast(list[RepositoryConfig], valid_repositories_fixt.value)
        ]

    with config_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    return config_file


# invalid:
# - not exist
# - exist but not a file
# - exist but not a yaml format
# - exist but not a valid config

# valid:
# - custom value
# - default value

# def test_create_from_config_file_valid(self,
#                                        patch_config_fixt: InputData,
#                                        patch_info_config_fixt: InputData,
#                                        valid_repositories_fixt: InputData,
#                                        ) -> None:
