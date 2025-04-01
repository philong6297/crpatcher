# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

__all__ = [
    "PatchGenError",
    "GitDiffError",
    "PatchWriteError",
    "IgnorePatternError",
    "StalePatchRemovalError",
]


class PatchGenError(Exception):
    pass


class InvalidGitRepoError(PatchGenError):
    pass


class GitDiffError(PatchGenError):
    pass


class PatchWriteError(PatchGenError):
    pass


class IgnorePatternError(PatchGenError):
    pass


class StalePatchRemovalError(PatchGenError):
    pass
