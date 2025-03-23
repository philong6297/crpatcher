# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Annotated, Callable, Optional

from git import Repo as GitPythonRepo
from git.exc import InvalidGitRepositoryError as GitPythonInvalidGitRepositoryError
from git.exc import NoSuchPathError as GitPythonNoSuchPathError

from crpatcher.base import CRPATCHER_STRICT_CONFIG
from crpatcher.config import PatchFileOption, PatchRequest
from crpatcher.patch_gen.exception import (
    GitRepoNotFoundError,
    InvalidGitRepoError,
    PatchDirCreationError,
    PatchWriteError,
)
from crpatcher.patch_gen.util import run_git_diff

_logger = logging.getLogger(__name__)


class GitPatchFileGenerator:
    def __init__(
        self,
        patch_request: PatchRequest,
        patch_opt: PatchFileOption,
    ):
        self._patch_opt = patch_opt
        self._patch_request = patch_request

        try:
            self._repo = GitPythonRepo(self._patch_request.repo_dir)
        except GitPythonNoSuchPathError as e:
            raise GitRepoNotFoundError("TODO(longlp): add error message") from e
        except GitPythonInvalidGitRepositoryError as e:
            raise InvalidGitRepoError("TODO(longlp): add error message") from e

        try:
            self._patch_request.patch_dir.mkdir(parents=True, exist_ok=True)
        except FileExistsError as e:
            raise PatchDirCreationError(f"TODO(longlp): add error message") from e

    def _get_modified_files(self) -> list[str]:
        cmd_output: str = run_git_diff(
            self._repo,
            [
                "--ignore-submodules",
                "--diff-filter=M",
                "--name-only",
                "--ignore-space-at-eol",
            ],
        )
        # cmd_output = run_git(
        #     self._patch_request.repo_dir,
        #     [
        #         "diff",
        #         "--ignore-submodules",
        #         "--diff-filter=M",
        #         "--name-only",
        #         "--ignore-space-at-eol",
        #     ],
        # )
        return [
            # Convert to posix so that we dont need to care about different path separators in cross platforms
            Path(stripped).as_posix()
            for line in cmd_output.splitlines()
            if (stripped := line.strip())
        ]

    def _write_patch_files(self, modified_files: list[str]) -> list[str]:
        # Format patch filename:
        # a/relative/path/to/repo/dir/modified_file.txt ->
        # a_relative_path_to_repo_dir_modified_file.txt.patch (if replacement_separator = "_")
        patch_file_names = [
            f"{posix_path.replace('/', self._patch_opt.replacement_separator)}"
            f".{self._patch_opt.ext}"
            for posix_path in modified_files
        ]

        patches_write_done_so_far = 0
        total_patches_to_write = len(modified_files)

        _logger.info(f"Writing {total_patches_to_write} .{self._patch_opt.ext} files:")

        for modified_file, patch_file_name in zip(modified_files, patch_file_names):
            patch_content = run_git_diff(
                self._repo,
                [
                    "--src-prefix=a/",
                    "--dst-prefix=b/",
                    "--full-index",
                    modified_file,
                ],
            )
            try:
                patch_file = self._patch_request.patch_dir.joinpath(patch_file_name)
                patch_file.write_text(
                    data=patch_content, encoding=self._patch_opt.encoding
                )
            except Exception as e:
                raise PatchWriteError(
                    f"Failed to write patch file {patch_file_name}: {e}"
                ) from e

            patches_write_done_so_far += 1
            _logger.info(
                f"----wrote {patches_write_done_so_far} / {total_patches_to_write}: {patch_file_name}"
            )

        return patch_file_names

    def remove_stale_patch_files(self, patch_filenames: list[str]) -> None:
        _logger.info(f"Removing stale .{self._patch_opt.ext} files:")

        try:
            existing_patch_files_in_patch_dir = [
                f.name
                for f in self._patch_request.patch_dir.glob(f"*.{self._patch_opt.ext}")
            ]
            valid_filenames = set(
                patch_filenames + self._patch_request.keep_patch_files
            )
            to_remove_filenames = [
                f for f in existing_patch_files_in_patch_dir if f not in valid_filenames
            ]

            if not to_remove_filenames:
                _logger.info("No stale .{self._patch_opt.ext} files to remove.")
                return

            remove_count = len(to_remove_filenames)
            for i, filename in enumerate(to_remove_filenames, 1):
                try:
                    (self._patch_request.patch_dir / filename).unlink()
                    _logger.info(f"----removed {i}/{remove_count}: {filename}")
                except Exception as e:
                    raise Exception(
                        f"Failed to remove stale patch file {filename}: {e}"
                    ) from e
        except Exception as e:
            raise Exception(f"Failed to process stale patch files: {e}") from e

    def update_patches(self) -> None:
        _logger.info(
            f"Updating patches for {self._patch_request.repo_dir}, saving to {self._patch_request.patch_dir}:"
        )
        try:
            modified_relative_paths = self._get_modified_files()
            if self._relative_paths_to_ignore_filter:
                modified_relative_paths = list(
                    filter(
                        self._relative_paths_to_ignore_filter, modified_relative_paths
                    )
                )

            patch_files = self._write_patch_files(modified_relative_paths)
            self.remove_stale_patch_files(patch_files)
        except Exception as e:
            raise Exception(f"Unexpected error during patch update: {e}") from e
