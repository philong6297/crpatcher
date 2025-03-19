# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, cast

import pytest
import json

from crpatcher.config import (
    CRPatcherConfig,
    PatchConfig,
    PatchInfoConfig,
    ProgramValidationContext,
    RepositoryConfig,
)
from tests.base.input_data import InputData, InputType

_CRPATCHER_CONFIG_DEFAULT_VALUES: Dict[str, Any] = {
    "patch_config": PatchConfig(),
    "patch_info_config": PatchInfoConfig(),
    "repositories": [],
}


@pytest.fixture(
    scope="class",
    params=[InputType.DEFAULT, InputType.CUSTOM],
    ids=[f"patch_config_{type}" for type in [InputType.DEFAULT, InputType.CUSTOM]],
)
def valid_patch_config_fixt(request: pytest.FixtureRequest) -> InputData:
    if request.param == InputType.DEFAULT:
        return InputData()

    # Custom input
    return InputData(
        value=PatchConfig(
            ext="custom_ext",
            encoding="ascii",
            replacement_separator="custom-replacement-separator",
        ),
        type=InputType.CUSTOM,
    )

    # No need to test invalid data since it will be validated by Pydantic, see src/crpatcher/config/patch_config.py


@pytest.fixture(
    scope="class",
    params=[InputType.DEFAULT, InputType.CUSTOM],
    ids=[f"patch_info_config_{type}" for type in [InputType.DEFAULT, InputType.CUSTOM]],
)
def valid_patch_info_config_fixt(request: pytest.FixtureRequest) -> InputData:
    if request.param == InputType.DEFAULT:
        return InputData()

    # Custom input
    return InputData(
        value=PatchInfoConfig(
            version=2,
            ext="custom_ext",
            encoding="ascii",
        ),
        type=InputType.CUSTOM,
    )

    # No need to test invalid data since it will be validated by Pydantic, see src/crpatcher/config/patch_info_config.py


@pytest.fixture(
    scope="class",
    params=[InputType.DEFAULT, InputType.CUSTOM],
    ids=[f"repositories_{type}" for type in [InputType.DEFAULT, InputType.CUSTOM]],
)
def valid_repositories_fixt(
    crpatcher_test_base_dir: Path,
    crpatcher_existing_empty_dir: Path,
    crpatcher_existing_empty_file: Path,
    request: pytest.FixtureRequest,
) -> InputData:
    if request.param == InputType.DEFAULT:
        return InputData()

    # Custom input

    valid_absolute_dir = crpatcher_existing_empty_dir
    valid_relative_dir = valid_absolute_dir.relative_to(crpatcher_test_base_dir)
    program_context = ProgramValidationContext(
        config_file=crpatcher_existing_empty_file
    )
    all_valid_repositories = [
        # all absolute paths
        RepositoryConfig(repo_dir=valid_absolute_dir, patch_dir=valid_absolute_dir),
        # 1 absolute, 1 relative
        RepositoryConfig.create_with_context(
            repo_dir=valid_absolute_dir,
            patch_dir=valid_relative_dir,
            program_context=program_context,
        ),
        RepositoryConfig.create_with_context(
            repo_dir=valid_relative_dir,
            patch_dir=valid_absolute_dir,
            program_context=program_context,
        ),
        # 2 relative
        RepositoryConfig.create_with_context(
            repo_dir=valid_relative_dir,
            patch_dir=valid_relative_dir,
            program_context=program_context,
        ),
    ]
    return InputData(
        value=all_valid_repositories,
        type=InputType.CUSTOM,
    )

    # no need to test invalid data since it will be validated by Pydantic, see src/crpatcher/config/repository_config.py


class TestCRPatcherConfig:
    def test_direct_construction(
        self,
        valid_patch_config_fixt: InputData,
        valid_patch_info_config_fixt: InputData,
        valid_repositories_fixt: InputData,
    ) -> None:
        # We dont need to test invalid input data when using direct construction
        # since it will be validated by each Field member.
        # Thus, this test should not expect any Error

        # Build kwargs dict only including non-DEFAULT fields
        kwargs: Dict[str, Any] = {}

        if valid_patch_config_fixt.type != InputType.DEFAULT:
            kwargs["patch_config"] = valid_patch_config_fixt.value
        if valid_patch_info_config_fixt.type != InputType.DEFAULT:
            kwargs["patch_info_config"] = valid_patch_info_config_fixt.value
        if valid_repositories_fixt.type != InputType.DEFAULT:
            kwargs["repositories"] = valid_repositories_fixt.value

        config = CRPatcherConfig(**kwargs)

        # For assertions, compare with value if not DEFAULT, otherwise use defaults
        assert config.patch_config == (
            valid_patch_config_fixt.value
            if valid_patch_config_fixt.type != InputType.DEFAULT
            else _CRPATCHER_CONFIG_DEFAULT_VALUES["patch_config"]
        )
        assert config.patch_info_config == (
            valid_patch_info_config_fixt.value
            if valid_patch_info_config_fixt.type != InputType.DEFAULT
            else _CRPATCHER_CONFIG_DEFAULT_VALUES["patch_info_config"]
        )
        assert config.repositories == (
            valid_repositories_fixt.value
            if valid_repositories_fixt.type != InputType.DEFAULT
            else _CRPATCHER_CONFIG_DEFAULT_VALUES["repositories"]
        )

    def test_create_from_config_file_valid(
        self,
        crpatcher_test_base_dir: Path,
        valid_patch_config_fixt: InputData,
        valid_patch_info_config_fixt: InputData,
        valid_repositories_fixt: InputData,
    ) -> None:
        valid_config_file = _create_valid_config_file(
            crpatcher_test_base_dir,
            valid_patch_config_fixt,
            valid_patch_info_config_fixt,
            valid_repositories_fixt,
        )

        config = CRPatcherConfig.create_from_config_file(valid_config_file)

        assert config.patch_config == (
            valid_patch_config_fixt.value
            if valid_patch_config_fixt.type != InputType.DEFAULT
            else _CRPATCHER_CONFIG_DEFAULT_VALUES["patch_config"]
        )

        assert config.patch_info_config == (
            valid_patch_info_config_fixt.value
            if valid_patch_info_config_fixt.type != InputType.DEFAULT
            else _CRPATCHER_CONFIG_DEFAULT_VALUES["patch_info_config"]
        )

        assert config.repositories == (
            valid_repositories_fixt.value
            if valid_repositories_fixt.type != InputType.DEFAULT
            else _CRPATCHER_CONFIG_DEFAULT_VALUES["repositories"]
        )


def _create_valid_config_file(
    crpatcher_test_base_dir: Path,
    valid_patch_config_fixt: InputData,
    valid_patch_info_config_fixt: InputData,
    valid_repositories_fixt: InputData,
) -> Path:
    # Construct the file name based on fixture states
    patch_config_name = f"patch_config_{'default' if valid_patch_config_fixt.type == InputType.DEFAULT else 'custom'}"
    patch_info_config_name = f"patch_info_config_{'default' if valid_patch_info_config_fixt.type == InputType.DEFAULT else 'custom'}"
    repositories_name = f"repositories_{'default' if valid_repositories_fixt.type == InputType.DEFAULT else 'custom'}"
    config_file_name = f"valid_config_{patch_config_name}_{patch_info_config_name}_{repositories_name}.yaml"
    # Define the path for the config file
    config_file = crpatcher_test_base_dir.joinpath(config_file_name)

    if config_file.is_file():
        raise FileExistsError(
            f"Config file {config_file.as_posix()} already exists. It should be not at the time of running this test"
        )

    data: dict[str, Any] = {}

    if valid_patch_config_fixt.type != InputType.DEFAULT:
        data["patch_config"] = cast(
            PatchConfig, valid_patch_config_fixt.value
        ).model_dump()

    if valid_patch_info_config_fixt.type != InputType.DEFAULT:
        data["patch_info_config"] = cast(
            PatchInfoConfig, valid_patch_info_config_fixt.value
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
#                                        valid_patch_config_fixt: InputData,
#                                        valid_patch_info_config_fixt: InputData,
#                                        valid_repositories_fixt: InputData,
#                                        ) -> None:
