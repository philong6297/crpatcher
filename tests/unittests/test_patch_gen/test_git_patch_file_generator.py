# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.


from pathlib import Path
import uuid
from contextlib import nullcontext

from git import Repo
import pytest

from crpatcher.patch_gen import GitPatchFileGenerator, InvalidGitRepoError, GitDiffError
from crpatcher.config import PatchRequest, PatchFileOption
from tests.base.pytest_cases import (
    pytest_cases_parametrize,
    pytest_cases_fixture,
    pytest_cases_fixture_ref,
)


@pytest_cases_fixture(scope="class")
def fixt_repo_dir(fixt_crpatcher_base_dir: Path):
    # Create random directory name
    random_dir_name = str(uuid.uuid4())
    repo_path = fixt_crpatcher_base_dir / random_dir_name

    # Initialize git repo
    repo = Repo.init(repo_path)

    # Create some initial files
    test_files = {
        "file1.txt": "initial content 1",
        "dir1/file2.txt": "initial content 2",
        "dir1/subdir/file3.txt": "initial content 3",
    }

    for file_path, content in test_files.items():
        full_path = repo_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        repo.index.add([str(full_path)])

    # Create initial commit
    repo.index.commit("Initial commit")

    return repo_path


@pytest_cases_parametrize(
    argnames="repo_dir, is_valid_repo",
    argvalues=[
        (pytest_cases_fixture_ref("fixt_crpatcher_existing_empty_dir"), False),
        (pytest_cases_fixture_ref("fixt_repo_dir"), True),
    ],
    ids=["invalid_repo", "valid_repo"],
)
def test_constructor(
    repo_dir: Path, is_valid_repo: bool, fixt_crpatcher_base_dir: Path
):
    with pytest.raises(InvalidGitRepoError) if not is_valid_repo else nullcontext():
        GitPatchFileGenerator(
            patch_request=PatchRequest(
                repo_dir=repo_dir, patch_dir=fixt_crpatcher_base_dir
            ),
            patch_file_option=PatchFileOption(),
        )


def test_get_modified_files(fixt_repo_dir: Path, fixt_crpatcher_base_dir: Path):
    # Modify some files in the repo
    file1_path = fixt_repo_dir / "file1.txt"
    file2_path = fixt_repo_dir / "dir1/file2.txt"

    # Modify existing files
    file1_path.write_text("modified content 1")
    file2_path.write_text("modified content 2")

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir, patch_dir=fixt_crpatcher_base_dir
        ),
        patch_file_option=PatchFileOption(),
    )

    modified_files = generator._get_modified_files()

    # Should detect both modified files
    assert len(modified_files) == 2
    assert file1_path in modified_files
    assert file2_path in modified_files


def test_generate_patches(fixt_repo_dir: Path, fixt_crpatcher_base_dir: Path):
    # Modify a file
    file1_path = fixt_repo_dir / "file1.txt"
    file1_path.write_text("modified content for patch test")

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir, patch_dir=fixt_crpatcher_base_dir
        ),
        patch_file_option=PatchFileOption(),
    )

    # Generate patches
    generator.update_patches()

    # Check if patch file was created
    expected_patch_file = fixt_crpatcher_base_dir / "file1.txt.patch"
    assert expected_patch_file.exists()

    # Verify patch content
    patch_content = expected_patch_file.read_text()
    assert "modified content for patch test" in patch_content
    assert "-initial content 1" in patch_content


def test_remove_stale_patches(fixt_repo_dir: Path, fixt_crpatcher_base_dir: Path):
    # Create a stale patch file
    stale_patch = fixt_crpatcher_base_dir / "stale.txt.patch"
    stale_patch.write_text("old patch content")

    # Modify a file to generate a new patch
    file1_path = fixt_repo_dir / "file1.txt"
    file1_path.write_text("new content")

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir, patch_dir=fixt_crpatcher_base_dir
        ),
        patch_file_option=PatchFileOption(),
    )

    # Update patches
    generator.update_patches()

    # Verify stale patch was removed
    assert not stale_patch.exists()
    # Verify new patch exists
    assert (fixt_crpatcher_base_dir / "file1.txt.patch").exists()


def test_ignore_patterns(fixt_repo_dir: Path, fixt_crpatcher_base_dir: Path):
    from pathspec import PathSpec

    # Modify multiple files
    (fixt_repo_dir / "file1.txt").write_text("modified 1")
    (fixt_repo_dir / "dir1/file2.txt").write_text("modified 2")

    # Create generator with ignore pattern
    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir,
            patch_dir=fixt_crpatcher_base_dir,
            ignore_patterns=["dir1/*"],
        ),
        patch_file_option=PatchFileOption(),
    )

    # Generate patches
    generator.update_patches()

    # Only file1.txt.patch should be created, dir1/file2.txt should be ignored
    assert (fixt_crpatcher_base_dir / "file1.txt.patch").exists()
    assert not (fixt_crpatcher_base_dir / "dir1_file2.txt.patch").exists()


def test_run_git_diff(fixt_repo_dir: Path, fixt_crpatcher_base_dir: Path, monkeypatch):
    from git.exc import GitCommandError
    from git.cmd import Git

    # Create a custom Git class that raises an error for diff
    class ErrorGit(Git):
        def diff(self, *args, **kwargs):
            raise GitCommandError("git diff", 128, "mock git diff error")

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir, patch_dir=fixt_crpatcher_base_dir
        ),
        patch_file_option=PatchFileOption(),
    )

    # fresh repo, no changes, should not raise error, output should be empty
    with nullcontext():
        output = generator._run_git_diff([])
        assert len(output) == 0

    # modify a file, should not raise error, output should be non-empty
    with nullcontext():
        # Modify multiple files
        (fixt_repo_dir / "file1.txt").write_text("modified 1")
        (fixt_repo_dir / "dir1/file2.txt").write_text("modified 2")
        output = generator._run_git_diff([])
        assert len(output) > 0

    # Replace the git instance with our error-raising version
    generator._repo.git = ErrorGit(generator._repo.working_dir)

    with pytest.raises(GitDiffError):
        generator._run_git_diff([])
