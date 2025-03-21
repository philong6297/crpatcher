from enum import Enum
from typing import Any, Callable, Generic, Self, Type, TypeVar, Union, cast

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


class Input(BaseModel, Generic[T]):
    data: Union[T, NoValue] = Field(default=NoValue())
    type: InputType = InputType.DEFAULT

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        strict=True,
    )

    @staticmethod
    def idgen_for_input_parametrize(expected_type: Type[Any]) -> Callable[..., str]:
        def _implement(**kwargs: dict[str, Any]) -> str:
            if len(kwargs) != 1:
                raise ValueError(
                    "Invalid **kwargs. "
                    "This function is only intended to use with @parametrize(`name`, list[Input[str]])."
                    f"Actual: {kwargs}"
                )

            name, input = next(iter(kwargs.items()))

            if not isinstance(input, Input):
                raise ValueError(
                    "Invalid value type."
                    f"This function is only intended to use with @parametrize(`name`, list[Input[{expected_type.__name__}]])."
                    f"Actual: {type(input)}"
                )

            casted_data = cast(Any, input.data)  # type: ignore

            if not isinstance(casted_data, (expected_type, NoValue)):
                raise ValueError(
                    "Invalid data type."
                    f"This function is only intended to use with @parametrize(`name`, list[Input[{expected_type.__name__}]])."
                    f"Actual: {type(casted_data).__name__}"
                )

            return f"({name}={input.type.name})"

        return _implement

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
