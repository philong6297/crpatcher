from pydantic import BaseModel, ConfigDict, Field


class A(BaseModel):
    a: int = Field(
        default=1,
        ge=1,
        allow_inf_nan=False,
    )

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        strict=True,
    )


instance = A(a=1)
instance.model_dump()
