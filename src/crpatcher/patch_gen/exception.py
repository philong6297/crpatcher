# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

__all__ = [
    "PatchGenError",
    "GitRepoNotFoundError",
    "InvalidGitRepoError",
    "GitDiffError",
    "PatchDirCreationError",
    "PatchWriteError",
    "IgnorePatternError",
    "StalePatchRemovalError",
]


class PatchGenError(Exception):
    pass


class GitRepoNotFoundError(PatchGenError):
    pass


class InvalidGitRepoError(PatchGenError):
    pass


class GitDiffError(PatchGenError):
    pass


class PatchDirCreationError(PatchGenError):
    pass


class PatchWriteError(PatchGenError):
    pass


class IgnorePatternError(PatchGenError):
    pass


class StalePatchRemovalError(PatchGenError):
    pass
