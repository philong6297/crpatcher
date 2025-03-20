# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from enum import Enum
from typing import Generic, Self, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InputType(Enum):
    DEFAULT = 0  # input parameter uses default value
    CUSTOM = 1  # explicitly set value
    INVALID = 2  # invalid value


class NoValue(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        strict=True,
    )


T = TypeVar("T")


class InputData(BaseModel, Generic[T]):
    value: Union[T, NoValue] = Field(default=NoValue())
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

    @property
    def safe_value(self) -> T:
        if isinstance(self.value, NoValue):
            raise ValueError("Value is NoValue")
        return self.value

    @model_validator(mode="after")
    def _validate(self) -> Self:
        # if type is default, value must be None
        if self.type == InputType.DEFAULT and not isinstance(self.value, NoValue):
            raise ValueError("When type is DEFAULT, value must be NoValue")

        # vice versa
        if isinstance(self.value, NoValue) and self.type != InputType.DEFAULT:
            raise ValueError("When value is NoValue, type must be DEFAULT")

        return self
