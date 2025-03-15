# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class GitCommandError(RuntimeError):
    """Exception raised when a git command fails."""

    def __init__(self, git_repo_dir: Path, git_args: list[str], err_msg: str):
        detail_err_msg = (
            f"Git command failed in {git_repo_dir}:{os.linesep}"
            f"Args: {' '.join(git_args)}{os.linesep}"
            f"{err_msg}{os.linesep}"
        )
        super().__init__(detail_err_msg)


def run_git(git_repo_dir: Path, git_args: list[str]) -> str:
    """
    Run a git command in the specified repository.

    Args:
        git_repo_dir: Path to the git repository directory
        git_args: List of git command arguments to execute

    Returns:
        The stdout output of the git command as a string

    Raises:
        GitCommandError: error raised when git command fails
    """

    if not git_repo_dir.is_dir():
        raise GitCommandError(
            git_repo_dir,
            git_args,
            err_msg="Git repository directory does not exist",
        )

    if not git_args:
        raise GitCommandError(
            git_repo_dir,
            git_args,
            err_msg="Git arguments cannot be empty",
        )

    if not shutil.which("git"):
        raise GitCommandError(
            git_repo_dir,
            git_args,
            err_msg="Git executable not found in PATH",
        )

    cmd = ["git"] + git_args

    try:
        result = subprocess.run(
            cmd,
            cwd=git_repo_dir,
            text=True,
            capture_output=True,
            check=True,  # raise an exception on non-zero return codes
        )
        return result.stdout
    except subprocess.CalledProcessError as err:
        err_msg = (
            f"Stdout: {err.stdout.strip()}{os.linesep}"
            f"Stderr: {err.stderr.strip()}{os.linesep}"
        )

        raise GitCommandError(
            git_repo_dir,
            git_args,
            err_msg,
        )
