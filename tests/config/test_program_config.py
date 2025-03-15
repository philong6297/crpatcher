# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from crpatcher.config import (
    PatchConfig,
    PatchInfoConfig,
    ProgramConfig,
    RepositoryConfig,
)


class TestProgramConfig:
    def test_load_config(self, tmp_path: Path) -> None:
        # Create test directories
        repo_dir = tmp_path / "repo"
        patch_dir = tmp_path / "patches"
        repo_dir.mkdir()
        patch_dir.mkdir()

        # Create test config file
        config_data = {
            "repositories": [
                {
                    "repo_dir": str(repo_dir),
                    "patch_dir": str(patch_dir),
                }
            ],
            "patchinfo_config": {
                "version": 2,
                "encoding": "ascii",
                "ext": "custom_info",
            },
            "patch_config": {
                "ext": "custom_patch",
                "encoding": "ascii",
                "replacement_separator": "underscore",
            },
        }
        config_file = tmp_path / "config.yaml"
        with config_file.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f)

        # Load and verify config
        config = ProgramConfig.load(config_file)

        # Verify repositories
        assert len(config.repositories) == 1
        repo_config = config.repositories[0]
        assert repo_config.repo_dir == repo_dir
        assert repo_config.patch_dir == patch_dir

        # Verify patchinfo config
        assert config.patchinfo_config.version == 2
        assert config.patchinfo_config.encoding == "ascii"
        assert config.patchinfo_config.ext == "custom_info"

        # Verify patch config
        assert config.patch_config.ext == "custom_patch"
        assert config.patch_config.encoding == "ascii"
        assert config.patch_config.replacement_separator == "underscore"

    def test_load_nonexistent_file(self) -> None:
        with pytest.raises(FileNotFoundError, match="File not found"):
            ProgramConfig.load("nonexistent.yaml")

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        # Create invalid YAML file
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content:", encoding="utf-8")

        with pytest.raises(yaml.YAMLError):
            ProgramConfig.load(config_file)

    def test_default_values(self, tmp_path: Path) -> None:
        # Create minimal config with just required fields
        repo_dir = tmp_path / "repo"
        patch_dir = tmp_path / "patches"
        repo_dir.mkdir()
        patch_dir.mkdir()

        config_data = {
            "repositories": [
                {
                    "repo_dir": str(repo_dir),
                    "patch_dir": str(patch_dir),
                }
            ],
        }
        config_file = tmp_path / "config.yaml"
        with config_file.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f)

        # Load and verify default values
        config = ProgramConfig.load(config_file)

        # Verify default patchinfo config
        assert config.patchinfo_config.version == 1
        assert config.patchinfo_config.encoding == "utf-8"
        assert config.patchinfo_config.ext == "patchinfo"

        # Verify default patch config
        assert config.patch_config.ext == "patch"
        assert config.patch_config.encoding == "utf-8"
        assert config.patch_config.replacement_separator == "-"
