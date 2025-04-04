# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.


import uuid
from contextlib import nullcontext
from pathlib import Path

import pytest
from git import Repo
from pytest_mock import MockerFixture

from crpatcher.config import PatchFileOption, PatchRequest
from crpatcher.patch_gen import GitDiffError, GitPatchFileGenerator, InvalidGitRepoError
from tests.base.pytest_cases import (
    pytest_cases_fixture,
    pytest_cases_fixture_ref,
    pytest_cases_parametrize,
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


def test_get_modified_files(
    fixt_repo_dir: Path,
    fixt_crpatcher_base_dir: Path,
    class_mocker: MockerFixture,
):
    # Modify some files in the repo
    file1_path = fixt_repo_dir / "file1.txt"
    file2_path = fixt_repo_dir / "dir1/file2.txt"

    # Modify existing files
    file1_path.write_text("modified content 1")
    file2_path.write_text("modified content 2")

    # 1. Test that the modified files are detected. No ignore patterns.

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir, patch_dir=fixt_crpatcher_base_dir
        ),
        patch_file_option=PatchFileOption(),
    )

    modified_files = generator._get_modified_files()

    # Should detect both modified files
    assert len(modified_files) == 2
    assert file1_path.relative_to(fixt_repo_dir) in modified_files
    assert file2_path.relative_to(fixt_repo_dir) in modified_files

    # 2. Test that the modified files are detected. With ignore patterns.

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir,
            patch_dir=fixt_crpatcher_base_dir,
            ignore_patterns=["dir1/*"],
        ),
        patch_file_option=PatchFileOption(),
    )

    modified_files = generator._get_modified_files()

    # Should detect only file1.txt
    assert len(modified_files) == 1
    assert file1_path.relative_to(fixt_repo_dir) in modified_files
    assert file2_path.relative_to(fixt_repo_dir) not in modified_files

    # 3. Any problem with the ignore pattern will raise IgnorePatternError
    from pathspec import PathSpec

    from crpatcher.patch_gen import IgnorePatternError

    mocked_match_files = class_mocker.patch.object(
        PathSpec, "match_files", side_effect=Exception("mock error")
    )
    with pytest.raises(IgnorePatternError):
        generator._get_modified_files()
    mocked_match_files.assert_called_once_with(
        {Path("file1.txt"), Path("dir1/file2.txt")}
    )
    class_mocker.stop(mocked_match_files)


def test_generate_patches(
    fixt_repo_dir: Path,
    fixt_crpatcher_base_dir: Path,
    class_mocker: MockerFixture,
):
    # Modify files
    file1 = fixt_repo_dir / "file1.txt"
    file1.write_text("modified file1")
    file2 = fixt_repo_dir / "dir1/file2.txt"
    file2.write_text("modified file2")
    file3 = fixt_repo_dir / "dir1/subdir/file3.txt"
    file3.write_text("modified file3")
    assert file1.is_file()
    assert file2.is_file()
    assert file3.is_file()

    # these files should not exist at this moment
    expected_patch1 = fixt_crpatcher_base_dir / "file1.txt.patch"
    expected_patch2 = fixt_crpatcher_base_dir / "dir1-file2.txt.patch"
    expected_patch3 = fixt_crpatcher_base_dir / "dir1-subdir-file3.txt.patch"
    assert not expected_patch1.exists()
    assert not expected_patch2.exists()
    assert not expected_patch3.exists()

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir, patch_dir=fixt_crpatcher_base_dir
        ),
        patch_file_option=PatchFileOption(),
    )

    from crpatcher.patch_gen import PatchWriteError

    # 1. invalid filepath should raise PatchWriteError, no patch file should be created
    with pytest.raises(PatchWriteError):
        generator._generate_patches([Path("not/existing/relative/path")])

    with pytest.raises(PatchWriteError):
        generator._generate_patches([fixt_repo_dir / "not/existing/absolute/path"])

    with pytest.raises(PatchWriteError):
        generator._generate_patches([fixt_repo_dir])  # directory

    # 2. valid filepath should generate .patch file with "-"" as separator
    result = generator._generate_patches(
        [
            file1,
            file2.relative_to(fixt_repo_dir),
            file3,
        ]
    )
    assert len(result) == 3
    assert expected_patch1.name in result
    assert expected_patch2.name in result
    assert expected_patch3.name in result
    assert expected_patch1.is_file()
    assert expected_patch2.is_file()
    assert expected_patch3.is_file()
    assert "modified file1" in expected_patch1.read_text()
    assert "modified file2" in expected_patch2.read_text()
    assert "modified file3" in expected_patch3.read_text()

    # 3. Any error during writing patch file, should raise PatchWriteError
    # remove all patch files for test 3
    expected_patch1.unlink()
    expected_patch2.unlink()
    expected_patch3.unlink()

    mocked_write_text = class_mocker.patch.object(
        Path, "write_text", side_effect=Exception("mock error")
    )

    # 3.1. test with absolute path
    with pytest.raises(PatchWriteError):
        generator._generate_patches([file1])
    mocked_write_text.assert_called_once()
    assert "modified file1" in mocked_write_text.call_args.kwargs["data"]
    assert mocked_write_text.call_args.kwargs["encoding"] == "utf-8"

    # 3.2. test with relative path
    mocked_write_text.reset_mock()
    with pytest.raises(PatchWriteError):
        generator._generate_patches([file1.relative_to(fixt_repo_dir)])
    mocked_write_text.assert_called_once()
    assert "modified file1" in mocked_write_text.call_args.kwargs["data"]
    assert mocked_write_text.call_args.kwargs["encoding"] == "utf-8"

    class_mocker.stop(mocked_write_text)


def test_remove_stale_patch_files(
    fixt_repo_dir: Path,
    fixt_crpatcher_base_dir: Path,
    class_mocker: MockerFixture,
):
    # Create a stale patch file
    stale_1 = fixt_crpatcher_base_dir / "stale_1.txt.patch"
    stale_1.write_text("old patch content 1")
    stale_2 = fixt_crpatcher_base_dir / "stale_2.txt.patch"
    stale_2.write_text("old patch content 2")
    stale_3 = fixt_crpatcher_base_dir / "stale_3.txt.patch"
    stale_3.write_text("old patch content 3")

    patch_1 = fixt_crpatcher_base_dir / "file1.txt.patch"
    patch_1.write_text("new patch content 1")
    patch_2 = fixt_crpatcher_base_dir / "file2.txt.patch"
    patch_2.write_text("new patch content 2")

    assert patch_1.is_file()
    assert patch_2.is_file()
    assert stale_1.is_file()
    assert stale_2.is_file()
    assert stale_3.is_file()

    # 1. Test all stale patch files are removed. No keep_patch_files.

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir,
            patch_dir=fixt_crpatcher_base_dir,
            keep_patch_files=[],
        ),
        patch_file_option=PatchFileOption(),
    )

    # Update patches
    generator._remove_stale_patch_files([patch_1.name, patch_2.name])

    # Verify stale patch was removed
    assert not stale_1.exists()
    assert not stale_2.exists()
    assert not stale_3.exists()
    assert patch_1.is_file()
    assert patch_2.is_file()

    # 2. Test some stale patch files are kept.

    # recover removed stale patches for test 2
    stale_1.write_text("new patch content 1")
    stale_2.write_text("new patch content 2")
    stale_3.write_text("new patch content 3")

    assert patch_1.is_file()
    assert patch_2.is_file()
    assert stale_1.is_file()
    assert stale_2.is_file()
    assert stale_3.is_file()

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir,
            patch_dir=fixt_crpatcher_base_dir,
            keep_patch_files=[stale_1.name, stale_2.name],
        ),
        patch_file_option=PatchFileOption(),
    )

    generator._remove_stale_patch_files([patch_1.name, patch_2.name])

    assert stale_1.is_file()
    assert stale_2.is_file()
    assert not stale_3.exists()
    assert patch_1.is_file()
    assert patch_2.is_file()

    # 3. Any error during removing stale patch files, should raise StalePatchRemovalError

    # recover removed stale patches for test 3
    stale_1.write_text("new patch content 1")
    stale_2.write_text("new patch content 2")
    stale_3.write_text("new patch content 3")

    assert patch_1.is_file()
    assert patch_2.is_file()
    assert stale_1.is_file()
    assert stale_2.is_file()
    assert stale_3.is_file()

    mocked_unlink = class_mocker.patch.object(
        Path, "unlink", side_effect=Exception("mock error")
    )

    from crpatcher.patch_gen import StalePatchRemovalError

    with pytest.raises(StalePatchRemovalError):
        generator._remove_stale_patch_files([patch_1.name, patch_2.name])
    mocked_unlink.assert_called_once_with()
    class_mocker.stop(mocked_unlink)

    # since raise error, so no patch files should be removed
    assert patch_1.is_file()
    assert patch_2.is_file()
    assert stale_1.is_file()
    assert stale_2.is_file()
    assert stale_3.is_file()

    # 4. Do nothing if there are no stales

    # remove all stales for test 4
    stale_1.unlink()
    stale_2.unlink()
    stale_3.unlink()

    assert patch_1.is_file()
    assert patch_2.is_file()
    assert not stale_1.exists()
    assert not stale_2.exists()
    assert not stale_3.exists()

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir,
            patch_dir=fixt_crpatcher_base_dir,
            keep_patch_files=[
                stale_1.name,
                stale_2.name,
                stale_3.name,
            ],  # even if all are kept, there should be no stales
        ),
        patch_file_option=PatchFileOption(),
    )

    generator._remove_stale_patch_files([patch_1.name, patch_2.name])

    assert patch_1.is_file()
    assert patch_2.is_file()
    assert not stale_1.exists()
    assert not stale_2.exists()
    assert not stale_3.exists()


def test_run_git_diff(
    fixt_repo_dir: Path, fixt_crpatcher_base_dir: Path, class_mocker: MockerFixture
):
    from git.cmd import Git
    from git.exc import GitCommandError

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir, patch_dir=fixt_crpatcher_base_dir
        ),
        patch_file_option=PatchFileOption(),
    )

    # 1. fresh repo, no changes, should not raise error, output should be empty
    with nullcontext():
        output = generator._run_git_diff([])
        assert len(output) == 0

    # 2. modify a file, should not raise error, output should be non-empty
    with nullcontext():
        # Modify multiple files
        (fixt_repo_dir / "file1.txt").write_text("modified 1")
        (fixt_repo_dir / "dir1/file2.txt").write_text("modified 2")
        output = generator._run_git_diff([])
        assert len(output) > 0

    # 3. Any git diff error, should raise GitDiffError

    # git.diff is actually git._call_process("diff", ...)
    # we only run the diff command here so it is safe to just set side_effect to _call_process
    mocked_call_process = class_mocker.patch.object(
        Git,
        "_call_process",
        side_effect=GitCommandError("git diff", 128, "mock git diff error"),
    )
    with pytest.raises(GitDiffError):
        generator._run_git_diff([])
    mocked_call_process.assert_called_once_with("diff")
    class_mocker.stop(mocked_call_process)


def test_update_patches(
    fixt_repo_dir: Path,
    fixt_crpatcher_base_dir: Path,
    class_mocker: MockerFixture,
):
    # Setup test files
    file1 = fixt_repo_dir / "file1.txt"
    file2 = fixt_repo_dir / "dir1/file2.txt"
    file1.write_text("modified file1")
    file2.write_text("modified file2")

    # Create a stale patch that should be removed
    stale_patch = fixt_crpatcher_base_dir / "stale.txt.patch"
    stale_patch.write_text("old patch content")

    # At this moment, there are 2 modified files and 1 stale patch
    assert stale_patch.is_file()
    assert file1.is_file()
    assert file2.is_file()

    generator = GitPatchFileGenerator(
        patch_request=PatchRequest(
            repo_dir=fixt_repo_dir,
            patch_dir=fixt_crpatcher_base_dir,
        ),
        patch_file_option=PatchFileOption(),
    )

    get_modified_files_mock = class_mocker.spy(
        generator,
        "_get_modified_files",
    )
    generate_patches_mock = class_mocker.spy(
        generator,
        "_generate_patches",
    )
    remove_stale_patches_mock = class_mocker.spy(
        generator,
        "_remove_stale_patch_files",
    )

    # Call update_patches
    generator.update_patches()

    # Verify flow
    get_modified_files_mock.assert_called_once()
    assert len(get_modified_files_mock.spy_return) == 2
    assert file1.relative_to(fixt_repo_dir) in get_modified_files_mock.spy_return
    assert file2.relative_to(fixt_repo_dir) in get_modified_files_mock.spy_return

    generate_patches_mock.assert_called_once_with(get_modified_files_mock.spy_return)
    assert len(generate_patches_mock.spy_return) == 2
    assert "file1.txt.patch" in generate_patches_mock.spy_return
    assert "dir1-file2.txt.patch" in generate_patches_mock.spy_return

    remove_stale_patches_mock.assert_called_once_with(generate_patches_mock.spy_return)

    # Verify result

    # Stale patch should be removed, new patch files should be created
    assert not stale_patch.exists()
    assert (fixt_crpatcher_base_dir / "file1.txt.patch").is_file()
    assert (fixt_crpatcher_base_dir / "dir1-file2.txt.patch").is_file()
    assert "modified file1" in (fixt_crpatcher_base_dir / "file1.txt.patch").read_text()
    assert (
        "modified file2"
        in (fixt_crpatcher_base_dir / "dir1-file2.txt.patch").read_text()
    )

    class_mocker.stop(get_modified_files_mock)
    class_mocker.stop(generate_patches_mock)
    class_mocker.stop(remove_stale_patches_mock)
