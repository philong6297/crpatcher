from __future__ import (
    annotations,
)  # without this, there will be error in static type-checking

from pydantic import BaseModel, Field, validate_call


class ClassA(BaseModel):

    field_a: int = Field(default=2)

    # EXPLICIT RETURN ClassA will leads to error at runtime
    @classmethod
    @validate_call
    def does_not_work_1(
        cls,
        field_a: int,
    ) -> ClassA:
        return cls(field_a=field_a)

    # EXPLICIT RETURN ClassA will leads to error at runtime
    @staticmethod
    @validate_call
    def does_not_work_2(
        field_a: int,
    ) -> ClassA:
        return ClassA(field_a=field_a)

    # NO ERROR
    @classmethod
    @validate_call
    def work_1(
        cls,
        field_a: int,
    ):
        return cls(field_a=field_a)

    # NO ERROR
    @staticmethod
    @validate_call
    def work_2(
        field_a: int,
    ):
        return ClassA(field_a=field_a)
