# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pydantic import ConfigDict

# TODO(longlp): can we make it as private?
CRPATCHER_STRICT_CONFIG_DICT = ConfigDict(
    extra="forbid",
    frozen=True,
    validate_assignment=True,
    strict=True,
    allow_inf_nan=False,
)

__all__ = ["CRPATCHER_STRICT_CONFIG_DICT"]
