# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from typing import Any

import pytest
from pydantic import ValidationError

from crpatcher.config import PatchInfoConfig


class TestPatchInfoConfig:
    def test_default_values(self) -> None:
        config = PatchInfoConfig()
        assert config.version == 1
        assert config.encoding == "utf-8"
        assert config.ext == "patchinfo"

    def test_custom_values(self) -> None:
        config = PatchInfoConfig(
            version=2,
            encoding="ascii",
            ext="custom_info",
        )
        assert config.version == 2
        assert config.encoding == "ascii"
        assert config.ext == "custom_info"

    @pytest.mark.parametrize(
        ("version", "error_msg"),
        [
            (0, "Input should be greater than or equal to 1"),
            (-1, "Input should be greater than or equal to 1"),
            (float("inf"), "Input should not be infinity or NaN"),
            (float("nan"), "Input should not be infinity or NaN"),
        ],
    )
    def test_invalid_version(self, version: Any, error_msg: str) -> None:
        with pytest.raises(ValidationError, match=error_msg):
            PatchInfoConfig(version=version)

    @pytest.mark.parametrize(
        "ext",
        [
            "invalid-ext",  # Contains hyphen
            "invalid.ext",  # Contains dot
            "invalid/ext",  # Contains slash
            "invalid ext",  # Contains space
            "invalid$ext",  # Contains special character
        ],
    )
    def test_invalid_ext(self, ext: str) -> None:
        with pytest.raises(ValidationError, match="String should match pattern"):
            PatchInfoConfig(ext=ext)
