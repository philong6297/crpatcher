# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

from typing import Any


class NoPublicConstructor(type):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise TypeError("no public constructor is allowed")

    def _create(self, *args: Any, **kwargs: Any) -> Any:
        return super().__call__(*args, **kwargs)
