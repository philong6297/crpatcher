# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

import pytest

from crpatcher.patch_gen import GitPatchFileGenerator

# repo
# 1. valid repo
# 2.invalid repo, an existing dir, but not a git repo
# 3.invalid repo, an existing dir, has .git dir, but not a git repo
# Do not need to test non existing dir, because it will be checked in PatchRequest constructor

# patch dir
# 1. valid patch dir, empty
# 2. valid patch dir, has valid files
# 3. invalid patch dir, existing dir, but has non-file: symlink, sub folder
# 4. invalid patch dir, existing dir, but has files with wrong extension

#


def test_constructor():
    pass
