# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import logging
from pathlib import Path

from git import Repo as GitPythonRepo
from git.exc import GitError as GitPythonError

from crpatcher.base.util import is_file_in_folder
from crpatcher.config import PatchFileOption, PatchRequest
from crpatcher.patch_gen.exception import (
    GitDiffError,
    IgnorePatternError,
    InvalidGitRepoError,
    PatchWriteError,
    StalePatchRemovalError,
)

_logger = logging.getLogger(__name__)


class GitPatchFileGenerator:
    def __init__(
        self,
        *,
        patch_request: PatchRequest,
        patch_file_option: PatchFileOption,
    ):
        self._patch_request = patch_request
        self._patch_file_option = patch_file_option

        try:
            self._repo = GitPythonRepo(self._patch_request.repo_dir)
        except GitPythonError as e:
            raise InvalidGitRepoError("TODO(longlp): add error message") from e

    def update_patches(self) -> None:
        _logger.info(
            f"Updating patches for {self._patch_request.repo_dir}, saving to {self._patch_request.patch_dir}:"
        )

        # 1. Get all modified files in the repo
        modified_files = self._get_modified_files()
        # 2. Write patch files
        patch_files = self._generate_patches(modified_files)
        # 3. Remove stale patch files
        self._remove_stale_patch_files(patch_files)

    def _generate_patches(self, filepaths: list[Path]) -> list[str]:
        # validate that all files are in the repo then generate corresponding patch filenames
        patch_file_names: list[str] = []
        for filepath in filepaths:
            if not is_file_in_folder(
                file_path=filepath, folder_path=self._patch_request.repo_dir
            ):
                raise PatchWriteError(f"TODO(longlp): add error message")

            # patch file name use relative path format
            if filepath.is_absolute():
                filepath = filepath.relative_to(self._patch_request.repo_dir)

            # Format patch filename:
            # a/relative/path/to/repo/dir/modified_file.txt ->
            # a_relative_path_to_repo_dir_modified_file.txt.patch (if replacement_separator = "_")
            # use posix to get rid of different OS path separators
            formatted_name = filepath.as_posix().replace(
                "/", self._patch_file_option.name_separator
            )
            patch_file_names.append(
                f"{formatted_name}"
                f".{self._patch_file_option.extension}"  # file extension
            )

        patches_write_done_so_far = 0
        total_patches_to_write = len(filepaths)

        _logger.info(
            f"Writing {total_patches_to_write} .{self._patch_file_option.extension} files:"
        )

        for filepath, patch_file_name in zip(filepaths, patch_file_names):

            patch_content = self._run_git_diff(
                [
                    "--src-prefix=a/",
                    "--dst-prefix=b/",
                    "--full-index",
                    filepath.as_posix(),
                ],
            )
            try:
                patch_file = self._patch_request.patch_dir / patch_file_name
                patch_file.write_text(
                    data=patch_content, encoding=self._patch_file_option.encoding
                )
            except Exception as e:
                raise PatchWriteError(f"TODO(longlp): add error message") from e

            patches_write_done_so_far += 1
            _logger.info(
                f"----wrote {patches_write_done_so_far} / {total_patches_to_write}: {patch_file_name}"
            )

        return patch_file_names

    def _remove_stale_patch_files(self, updated_patch_filenames: list[str]) -> None:
        _logger.info(f"Removing stale .{self._patch_file_option.extension} files:")

        existing_patch_files = {
            f.name
            for f in self._patch_request.patch_dir.glob(
                f"*.{self._patch_file_option.extension}"
            )
        }
        patch_files_to_keep = set(
            updated_patch_filenames + self._patch_request.keep_patch_files
        )
        to_remove_filenames = [
            f for f in existing_patch_files if f not in patch_files_to_keep
        ]

        if not to_remove_filenames:
            _logger.info(
                f"No stale .{self._patch_file_option.extension} files to remove."
            )
            return

        remove_count = len(to_remove_filenames)
        for i, filename in enumerate(to_remove_filenames, 1):
            try:
                (self._patch_request.patch_dir / filename).unlink()
                _logger.info(f"----removed {i}/{remove_count}: {filename}")
            except Exception as e:
                raise StalePatchRemovalError(
                    f"Failed to remove stale patch file {filename}: {e}"
                ) from e

    # return relative paths of modified files
    def _get_modified_files(self) -> list[Path]:
        cmd_output: str = self._run_git_diff(
            [
                "--ignore-submodules",
                "--diff-filter=M",
                "--name-only",
                "--ignore-space-at-eol",
            ],
        )
        # use set to be friendly with step 2
        modified_relative_files = {
            Path(line.strip()) for line in cmd_output.splitlines()
        }

        # 2. Ignore files based on config
        try:
            if self._patch_request.ignore_pattern_matcher is not None:
                files_to_ignore = list(
                    self._patch_request.ignore_pattern_matcher.match_files(
                        modified_relative_files
                    )
                )

                for file in files_to_ignore:
                    modified_relative_files.discard(Path(file))
        except Exception as e:
            raise IgnorePatternError(f"TODO(longlp): add error message") from e

        return list(modified_relative_files)

    def _run_git_diff(self, args: list[str]) -> str:
        try:
            return self._repo.git.diff(*args)
        except Exception as e:
            raise GitDiffError(f"Failed to run git diff with args {args}: {e}") from e
