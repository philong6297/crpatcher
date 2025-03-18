# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from contextlib import nullcontext
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml
from pydantic import ValidationError

from crpatcher.config import (
    CRPatcherConfig,
    PatchConfig,
    PatchInfoConfig,
    ProgramValidationContext,
    RepositoryConfig,
)
from tests.base.input_data import InputData, InputType


@pytest.fixture(scope="class", params=[InputType.DEFAULT, InputType.CUSTOM])
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


@pytest.fixture(scope="class", params=[InputType.DEFAULT, InputType.CUSTOM])
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


@pytest.fixture(scope="class", params=[InputType.DEFAULT, InputType.CUSTOM])
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


@pytest.fixture(scope="class")
def config_file_fixture(
    crpatcher_test_base_dir: Path,
    crpatcher_existing_empty_dir: Path,
) -> Path:
    config_file = crpatcher_test_base_dir / "config.yaml"
    config_data = {
        "patch_config": {
            "ext": "custom_ext",
            "encoding": "ascii",
            "replacement_separator": "custom-replacement-separator",
        },
        "patch_info_config": {
            "version": 2,
            "ext": "custom_ext",
            "encoding": "ascii",
        },
        "repositories": [
            {
                "repo_dir": str(crpatcher_existing_empty_dir),
                "patch_dir": str(crpatcher_existing_empty_dir),
            }
        ],
    }
    with config_file.open("w", encoding="utf-8") as f:
        yaml.dump(config_data, f)
    return config_file


class TestCRPatcherConfig:
    def test_create_from_config_file(
        self,
        config_file_fixture: Path,
        crpatcher_existing_empty_dir: Path,
    ) -> None:
        config = CRPatcherConfig.create_from_config_file(config_file_fixture)

        # Verify patch config
        assert config.patch_config.ext == "custom_ext"
        assert config.patch_config.encoding == "ascii"
        assert (
            config.patch_config.replacement_separator == "custom-replacement-separator"
        )

        # Verify patch info config
        assert config.patch_info_config.version == 2
        assert config.patch_info_config.ext == "custom_ext"
        assert config.patch_info_config.encoding == "ascii"

        # Verify repository config
        assert len(config.repositories) == 1
        assert config.repositories[0].repo_dir == crpatcher_existing_empty_dir
        assert config.repositories[0].patch_dir == crpatcher_existing_empty_dir

    def test_create_from_config_file_not_found(
        self,
        crpatcher_non_existent_file: Path,
    ) -> None:
        with pytest.raises(FileNotFoundError):
            CRPatcherConfig.create_from_config_file(crpatcher_non_existent_file)

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

        DEFAULT_VALUES: Dict[str, Any] = {
            "patch_config": PatchConfig(),
            "patch_info_config": PatchInfoConfig(),
            "repositories": [],
        }

        config = CRPatcherConfig(**kwargs)

        # For assertions, compare with value if not DEFAULT, otherwise use defaults
        assert config.patch_config == (
            valid_patch_config_fixt.value
            if valid_patch_config_fixt.type != InputType.DEFAULT
            else DEFAULT_VALUES["patch_config"]
        )
        assert config.patch_info_config == (
            valid_patch_info_config_fixt.value
            if valid_patch_info_config_fixt.type != InputType.DEFAULT
            else DEFAULT_VALUES["patch_info_config"]
        )
        assert config.repositories == (
            valid_repositories_fixt.value
            if valid_repositories_fixt.type != InputType.DEFAULT
            else DEFAULT_VALUES["repositories"]
        )


# invalid:
# - not exist
# - exist but not a file
# - exist but not a yaml format
# - exist but not a valid config

# valid:
# - custom value
# - default value
