import itertools

from pydantic import BaseModel, ConfigDict, Field

from crpatcher.base.util import CRPATCHER_STRICT_CONFIG


class _ArgBuilder(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        strict=True,
        allow_inf_nan=False,
        validate_default=True,
    )

    A: tuple[int, ...] = (1, 2, 3, 4)


ARG_BUILDER = _ArgBuilder(A=(5,))

print(ARG_BUILDER.A)  # [2]
ARG_BUILDER.A.append(2)
print(ARG_BUILDER.A)  # [2]
