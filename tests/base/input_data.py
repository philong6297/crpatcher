# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self


class InputType(Enum):
    DEFAULT = 0
    CUSTOM = 1
    INVALID = 2


class InputData(BaseModel):
    value: Any = None
    type: InputType = InputType.DEFAULT

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        strict=True,
    )

    @property
    def should_raise_error(self) -> bool:
        return self.type == InputType.INVALID

    @model_validator(mode="after")
    def _validate(self) -> Self:
        # if value is None, type must be DEFAULT, and vice versa
        if self.value is None and self.type != InputType.DEFAULT:
            raise ValueError("When value is None, type must be DEFAULT")
        if self.value is not None and self.type == InputType.DEFAULT:
            raise ValueError("When type is DEFAULT, value must be None")
        return self
