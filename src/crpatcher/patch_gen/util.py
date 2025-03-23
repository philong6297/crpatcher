# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

import git

from crpatcher.patch_gen.exception import GitDiffError

__all__ = ["run_git_diff"]


def run_git_diff(repo: git.Repo, args: list[str]) -> str:
    try:
        return repo.git.diff(*args)
    except Exception as e:
        raise GitDiffError(f"Failed to run git diff with args {args}: {e}") from e
