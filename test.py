from __future__ import annotations

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, validate_call


def is_even(value: int) -> int:
    if value % 2 == 1:
        raise ValueError(f"{value} is not an even number")
    return value + 1


class Test(BaseModel):
    @validate_call(config=ConfigDict(strict=True, validate_default=True))
    def test(
        self,
        a: Annotated[list[str], Field(gt=1), AfterValidator(is_even)] = Field(
            default_factory=list
        ),
    ):
        return a


t = Test()
print(t.test())  # expect 4 + 1 = 5
print(t.test(2))  # expect 2 + 1 = 3
print(t.test(3))  # expect error
print(t.test(-1))  # expect error
print(t.test(0))  # expect error
print(t.test(0))  # expect error
print(t.test(0))  # expect error
