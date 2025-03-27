# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import os
from pathlib import Path

import pytest
from git import Repo

from crpatcher.config import PatchFileOption, PatchRequest


@pytest.fixture(scope="class")
def git_repo_dir_fixt(fixt_crpatcher_base_dir: Path) -> Path:
    """Create a temporary Git repository with some test files and modifications.

    The repository will have the following structure:
    - src/
      - main.py (modified)
      - utils.py (modified)
    - tests/
      - test_main.py (modified)
    - README.md (modified)
    """
    # Create a new Git repository
    repo_dir = fixt_crpatcher_base_dir.joinpath("repo").absolute()
    repo_dir.mkdir(parents=True, exist_ok=True)
    repo = Repo.init(repo_dir)

    # Create files
    repo_dir.joinpath("src").mkdir()
    repo_dir.joinpath("src", "main.py").write_text(
        f"def main():{os.linesep}    print('Hello'){os.linesep}"
    )
    repo_dir.joinpath("src", "utils.py").write_text(
        f"def helper():{os.linesep}    pass{os.linesep}"
    )

    repo_dir.joinpath("tests").mkdir()
    repo_dir.joinpath("tests", "test_main.py").write_text(
        f"def test_main():{os.linesep}    assert True{os.linesep}"
    )

    repo_dir.joinpath("README.md").write_text(f"# Test Repo{os.linesep}")

    # Add and commit initial files
    repo.index.add(["src/", "tests/", "README.md"])  # pyright: ignore[reportUnknownMemberType]
    repo.index.commit("Initial commit")

    return repo_dir


@pytest.fixture
def patch_request(temp_git_repo: Repo) -> PatchRequest:
    """Create a PatchRequest instance for testing."""
    repo_dir = Path(temp_git_repo.working_dir)
    return PatchRequest(
        repo_dir=repo_dir,
        patch_dir=repo_dir / "patches",
        ignore_patterns=["*.pyc", "__pycache__/*"],
        keep_patch_files=["README.md.patch"],
    )


@pytest.fixture
def patch_opt() -> PatchFileOption:
    """Create a PatchFileOption instance for testing."""
    return PatchFileOption(
        ext="patch",
        encoding="utf-8",
        replacement_separator="_",
    )
