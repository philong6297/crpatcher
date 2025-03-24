# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import logging
from pathlib import Path

from git import Repo as GitPythonRepo
from git.exc import InvalidGitRepositoryError as GitPythonInvalidGitRepositoryError
from git.exc import NoSuchPathError as GitPythonNoSuchPathError
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

from crpatcher.config import PatchFileOption, PatchRequest
from crpatcher.patch_gen.exception import (
    GitRepoNotFoundError,
    IgnorePatternError,
    InvalidGitRepoError,
    PatchDirCreationError,
    PatchWriteError,
    StalePatchRemovalError,
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

        # Validate patch directory requirements
        # Check for non-files and wrong extensions
        try:
            for p in self._patch_request.patch_dir.iterdir():
                if not p.is_file():
                    raise PatchDirCreationError(f"TODO(longlp): add error message")
                if p.suffix != f".{self._patch_opt.ext}":
                    raise PatchDirCreationError(f"TODO(longlp): add error message")

        except Exception as e:
            raise PatchDirCreationError(f"TODO(longlp): add error message") from e

        if not self._patch_request.ignore_patterns:
            self._ignore_spec = None
        else:
            try:
                self._ignore_spec = PathSpec.from_lines(
                    GitWildMatchPattern, self._patch_request.ignore_patterns
                )
            except Exception as e:
                raise IgnorePatternError(f"TODO(longlp): add error message") from e

    def _write_patch_files(self, modified_absolute_filepaths: list[Path]) -> list[str]:
        # validate that all files are in the repo then generate corresponding patch filenames
        patch_file_names: list[str] = []
        for filepath in modified_absolute_filepaths:
            if (
                not filepath.is_file()
                or self._patch_request.repo_dir not in filepath.parents
            ):
                raise PatchWriteError(f"TODO(longlp): add error message")

            # Format patch filename:
            # a/relative/path/to/repo/dir/modified_file.txt ->
            # a_relative_path_to_repo_dir_modified_file.txt.patch (if replacement_separator = "_")
            formatted_name = (
                filepath.relative_to(
                    self._patch_request.repo_dir
                )  # convert to relative path as we dont need to include the repo dir in the filename
                .as_posix()  # use posix to get rid of different OS path separators
                .replace(
                    "/", self._patch_opt.replacement_separator
                )  # replace slashes with replacement_separator
            )
            filename = (
                f"{formatted_name}"
                f".{self._patch_opt.ext}"  # file extension
            )
            patch_file_names.append(filename)

        patches_write_done_so_far = 0
        total_patches_to_write = len(modified_absolute_filepaths)

        _logger.info(f"Writing {total_patches_to_write} .{self._patch_opt.ext} files:")

        for modified_file, patch_file_name in zip(
            modified_absolute_filepaths, patch_file_names
        ):
            relative_filepath = modified_file.relative_to(self._patch_request.repo_dir)
            patch_content = run_git_diff(
                self._repo,
                [
                    "--src-prefix=a/",
                    "--dst-prefix=b/",
                    "--full-index",
                    relative_filepath.as_posix(),
                ],
            )
            try:
                patch_file = self._patch_request.patch_dir.joinpath(patch_file_name)
                patch_file.write_text(
                    data=patch_content, encoding=self._patch_opt.encoding
                )
            except Exception as e:
                raise PatchWriteError(f"TODO(longlp): add error message") from e

            patches_write_done_so_far += 1
            _logger.info(
                f"----wrote {patches_write_done_so_far} / {total_patches_to_write}: {patch_file_name}"
            )

        return patch_file_names

    def remove_stale_patch_files(self, updated_patch_filenames: list[str]) -> None:
        _logger.info(f"Removing stale .{self._patch_opt.ext} files:")

        existing_patch_files = {
            f.name
            for f in self._patch_request.patch_dir.glob(f"*.{self._patch_opt.ext}")
        }
        patch_files_to_keep = set(
            updated_patch_filenames + self._patch_request.keep_patch_files
        )
        to_remove_filenames = [
            f for f in existing_patch_files if f not in patch_files_to_keep
        ]

        if not to_remove_filenames:
            _logger.info(f"No stale .{self._patch_opt.ext} files to remove.")
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

    def _get_modified_absolute_filepaths(self) -> list[Path]:
        cmd_output: str = run_git_diff(
            self._repo,
            [
                "--ignore-submodules",
                "--diff-filter=M",
                "--name-only",
                "--ignore-space-at-eol",
            ],
        )
        modified_relative_files = {
            self._patch_request.repo_dir.joinpath(stripped).resolve(
                strict=True,  # Raise OSError if cannot resolve. TODO(longlp): catch this
            )  # Convert to absolute to be friendly with step 2
            for line in cmd_output.splitlines()
            if (stripped := line.strip())
        }

        # 2. Ignore files based on config
        try:
            if self._ignore_spec is not None:
                files_to_ignore = self._ignore_spec.match_files(modified_relative_files)
                for file in files_to_ignore:
                    modified_relative_files.discard(Path(file))
        except Exception as e:
            raise IgnorePatternError(f"TODO(longlp): add error message") from e

        return list(modified_relative_files)

    def update_patches(self) -> None:
        _logger.info(
            f"Updating patches for {self._patch_request.repo_dir}, saving to {self._patch_request.patch_dir}:"
        )

        # 1. Get all modified files in the repo
        modified_files = self._get_modified_absolute_filepaths()
        # 2. Write patch files
        patch_files = self._write_patch_files(modified_files)
        # 3. Remove stale patch files
        self.remove_stale_patch_files(patch_files)
