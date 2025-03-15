# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pathlib import Path

import pytest
from pydantic import ValidationInfo

from crpatcher.config import ProgramValidationContext, RepositoryConfig


class TestRepositoryConfig:
    def test_absolute_paths(self, tmp_path: Path) -> None:
        # Create test directories
        repo_dir = tmp_path / "repo"
        patch_dir = tmp_path / "patches"
        repo_dir.mkdir()
        patch_dir.mkdir()

        # Create validation context
        context = ProgramValidationContext(config_file=tmp_path / "config.yaml")

        # Test with absolute paths
        config = RepositoryConfig(
            repo_dir=repo_dir,
            patch_dir=patch_dir,
        )
        config = config._resolve_directories(ValidationInfo(context=context))

        assert config.repo_dir == repo_dir
        assert config.patch_dir == patch_dir

    def test_relative_paths(self, tmp_path: Path) -> None:
        # Create test directories
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        repo_dir = base_dir / "repo"
        patch_dir = base_dir / "patches"
        repo_dir.mkdir()
        patch_dir.mkdir()

        # Create validation context with config file in base_dir
        context = ProgramValidationContext(config_file=base_dir / "config.yaml")

        # Test with relative paths
        config = RepositoryConfig(
            repo_dir=Path("repo"),
            patch_dir=Path("patches"),
        )
        config = config._resolve_directories(ValidationInfo(context=context))

        assert config.repo_dir == repo_dir
        assert config.patch_dir == patch_dir

    def test_missing_directories(self, tmp_path: Path) -> None:
        context = ProgramValidationContext(config_file=tmp_path / "config.yaml")

        # Test with non-existent directories
        config = RepositoryConfig(
            repo_dir=tmp_path / "nonexistent_repo",
            patch_dir=tmp_path / "nonexistent_patches",
        )

        with pytest.raises(ValueError, match="Repository directory not found"):
            config._resolve_directories(ValidationInfo(context=context))

        # Create repo dir but not patch dir
        (tmp_path / "nonexistent_repo").mkdir()
        with pytest.raises(ValueError, match="Patch directory not found"):
            config._resolve_directories(ValidationInfo(context=context))

    def test_missing_context(self, tmp_path: Path) -> None:
        config = RepositoryConfig(
            repo_dir=tmp_path,
            patch_dir=tmp_path,
        )

        with pytest.raises(ValueError, match="Missing program validation context"):
            config._resolve_directories(ValidationInfo(context=None))
