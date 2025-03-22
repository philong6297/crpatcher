# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Callable, Optional

from crpatcher.base import run_git
from crpatcher.config import PatchFileOption, PatchRequest

_logger = logging.getLogger(__name__)


class GitPatchGenerator:
    def __init__(
        self,
        patch_request: PatchRequest,
        patch_opt: PatchFileOption,
        relative_paths_to_ignore: Optional[Callable[[str], bool]] = None,
        patch_files_to_keep: Optional[list[str]] = None,
    ):
        self._git_repo_dir = patch_request.repo_dir
        self._patch_dir = patch_request.patch_dir
        self._relative_paths_to_ignore_filter = relative_paths_to_ignore
        self._patch_files_to_keep = patch_files_to_keep or []
        self._patch_opt = patch_opt

    def get_modified_relative_paths(self) -> list[str]:
        try:
            cmd_output = run_git(
                self._git_repo_dir,
                [
                    "diff",
                    "--ignore-submodules",
                    "--diff-filter=M",
                    "--name-only",
                    "--ignore-space-at-eol",
                ],
            )
            return [line.strip() for line in cmd_output.split(os.linesep) if line]
        except Exception as e:
            raise Exception(f"Failed to get modified paths: {e}") from e

    def write_patch_files(self, modified_relative_paths: list[str]) -> list[str]:
        try:
            self._patch_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise Exception(f"Failed to create patch directory: {e}") from e

        # Format patch filenames
        patch_filenames = [
            Path(relative_path)
            .as_posix()
            .replace("/", self._patch_opt.replacement_separator)
            + f".{self._patch_opt.ext}"
            for relative_path in modified_relative_paths
        ]

        write_ops_done_count = 0
        patch_count = len(modified_relative_paths)

        _logger.info(f"Writing {patch_count} .patch files:")
        for modified_file, patch_filename in zip(
            modified_relative_paths, patch_filenames
        ):
            try:
                per_file_patch_content = run_git(
                    self._git_repo_dir,
                    [
                        "diff",
                        "--src-prefix=a/",
                        "--dst-prefix=b/",
                        "--full-index",
                        modified_file,
                    ],
                )
                patch_file = self._patch_dir.joinpath(patch_filename)
                patch_file.write_text(per_file_patch_content)

                write_ops_done_count += 1
                _logger.info(
                    f"----wrote {write_ops_done_count} / {patch_count}: {patch_filename}"
                )
            except Exception as e:
                raise Exception(
                    f"Failed to write patch file {patch_filename}: {e}"
                ) from e

        return patch_filenames

    def remove_stale_patch_files(self, patch_filenames: list[str]) -> None:
        if not self._patch_dir.exists():
            _logger.error(f"Path at {self._patch_dir} does not exist.")
            return

        _logger.info("Remove stale .patch files if needed:")

        try:
            existing_patch_filenames = [f.name for f in self._patch_dir.glob("*.patch")]
            valid_filenames = set(patch_filenames + self._patch_files_to_keep)
            to_remove_filenames = [
                f for f in existing_patch_filenames if f not in valid_filenames
            ]

            if not to_remove_filenames:
                _logger.info("No stale .patch files to remove.")
                return

            remove_count = len(to_remove_filenames)
            for i, filename in enumerate(to_remove_filenames, 1):
                try:
                    (self._patch_dir / filename).unlink()
                    _logger.info(f"----removed {i}/{remove_count}: {filename}")
                except Exception as e:
                    raise Exception(
                        f"Failed to remove stale patch file {filename}: {e}"
                    ) from e
        except Exception as e:
            raise Exception(f"Failed to process stale patch files: {e}") from e

    def update_patches(self) -> None:
        _logger.info(
            f"Updating patches for {self._git_repo_dir}, saving to {self._patch_dir}:"
        )
        try:
            modified_relative_paths = self.get_modified_relative_paths()
            if self._relative_paths_to_ignore_filter:
                modified_relative_paths = list(
                    filter(
                        self._relative_paths_to_ignore_filter, modified_relative_paths
                    )
                )

            patch_files = self.write_patch_files(modified_relative_paths)
            self.remove_stale_patch_files(patch_files)
        except Exception as e:
            raise Exception(f"Unexpected error during patch update: {e}") from e
