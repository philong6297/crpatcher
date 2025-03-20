# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import json
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Dict, cast

import pytest
from pydantic import ValidationError
from crpatcher.config import (
    CRPatcherConfig,
    PatchConfig,
    PatchInfoConfig,
    RepositoryConfig,
)
from tests.base.input_data import InputData, InputType
from tests.unittests.config._test_crpatcher_config_inc import *


class TestCRPatcherConfig:
    def test_direct_construction(
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

        expected_config = CRPATCHER_CONFIG_DEFAULT()

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

    def test_create_from_existing_config_file(
        self,
        crpatcher_test_base_dir: Path,
        patch_config_fixt: InputData[PatchConfigTestData],
        patch_info_config_fixt: InputData[PatchInfoConfigTestData],
        repositories_fixt: InputData[list[RepositoryTestData]],
    ) -> None:
        valid_config_file = _create_config_file(
            crpatcher_test_base_dir,
            patch_config_fixt,
            patch_info_config_fixt,
            repositories_fixt,
        )

        should_raise_error = (
            patch_config_fixt.should_raise_error
            or patch_info_config_fixt.should_raise_error
            or repositories_fixt.should_raise_error
        )

        expected_context = (
            pytest.raises(ValidationError) if should_raise_error else nullcontext()
        )

        with expected_context:
            config = CRPatcherConfig.create_from_config_file(valid_config_file)

            if not should_raise_error:
                expected_config = CRPATCHER_CONFIG_DEFAULT()

                if patch_config_fixt.type != InputType.DEFAULT:
                    expected_config["patch_config"] = (
                        patch_config_fixt.safe_value.build_patch_config()
                    )

                if patch_info_config_fixt.type != InputType.DEFAULT:
                    expected_config["patch_info_config"] = (
                        patch_info_config_fixt.safe_value.build_patch_info_config()
                    )

                if repositories_fixt.type != InputType.DEFAULT:
                    expected_config["repositories"] = [
                        repository_data.build_repository_config()
                        for repository_data in repositories_fixt.safe_value
                    ]

                assert config.patch_config == expected_config["patch_config"]
                assert config.patch_info_config == expected_config["patch_info_config"]
                assert config.repositories == expected_config["repositories"]


def _create_config_file(
    crpatcher_test_base_dir: Path,
    patch_config_fixt: InputData[PatchConfigTestData],
    patch_info_config_fixt: InputData[PatchInfoConfigTestData],
    repositories_fixt: InputData[list[RepositoryTestData]],
) -> Path:
    # Construct the file name based on fixture states
    patch_config_name = f"patch_config_{patch_config_fixt.type.name}"
    patch_info_config_name = f"patch_info_config_{patch_info_config_fixt.type.name}"
    repositories_name = f"repositories_{repositories_fixt.type.name}"

    config_file_name = (
        f"{patch_config_name}_{patch_info_config_name}_{repositories_name}.json"
    )
    # Define the path for the config file
    config_file = crpatcher_test_base_dir.joinpath(config_file_name)

    if config_file.is_file():
        raise FileExistsError(
            f"Config file {config_file.as_posix()} already exists. It should be not at the time of running this test"
        )

    data: dict[str, Any] = {}

    if patch_config_fixt.type != InputType.DEFAULT:
        data["patch_config"] = patch_config_fixt.safe_value._asdict()
    if patch_info_config_fixt.type != InputType.DEFAULT:
        data["patch_info_config"] = patch_info_config_fixt.safe_value._asdict()

    if repositories_fixt.type != InputType.DEFAULT:
        data["repositories"] = [
            # RepositoryConfig contains pathlib.Path, which is not serializable by default
            {
                "repo_dir": repo.repo_dir.safe_value.path.as_posix(),
                "patch_dir": repo.patch_dir.safe_value.path.as_posix(),
            }
            for repo in repositories_fixt.safe_value
        ]

    with config_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    return config_file


# invalid file:
# - not exist TODO(longlp)
# - exist but not a file TODO(longlp)
# - exist but not a yaml format TODO(longlp)
# - exist but not a valid config DONE

# valid:
# - custom value DONE
# - default value DONE

#
