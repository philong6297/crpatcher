# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from enum import Enum
from typing import Any, Generic, Self, TypeVar, Union, get_args

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator


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


class Input(BaseModel, Generic[T]):
    data: Union[T, NoValue] = Field(default=NoValue())
    type: InputType = InputType.DEFAULT

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        strict=True,
    )

    _data_type: type = PrivateAttr(None)

    def model_post_init(self, __context: Any) -> None:
        # Extract the type argument T at runtime from __orig_class__
        # return Input[T]
        orig_class = getattr(self, "__orig_class__", None)
        if orig_class:
            # return [T, ...]
            args = get_args(orig_class)
            # Since there is only one type argument, first one must be T
            if args:
                self._data_type = args[0]

    @property
    def data_type(self):
        return self._data_type

    @property
    def is_invalid_data(self) -> bool:
        return self.type == InputType.INVALID

    @property
    def safe_data(self) -> T:
        if isinstance(self.data, NoValue):
            raise ValueError("Value is NoValue")
        return self.data

    @model_validator(mode="after")
    def _validate(self) -> Self:
        # if type is default, value must be None
        if self.type == InputType.DEFAULT and not isinstance(self.data, NoValue):
            raise ValueError("When type is DEFAULT, value must be NoValue")

        # vice versa
        if isinstance(self.data, NoValue) and self.type != InputType.DEFAULT:
            raise ValueError("When value is NoValue, type must be DEFAULT")

        return self
