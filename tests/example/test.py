import itertools

from pydantic import BaseModel, ConfigDict, Field

from tests.base.pytest_cases import *


@pytest_cases_parametrize(
    a=[1, 2, 3],
    b=[4, 5, 6],
)
def test_a(a: int, b: int) -> None:
    assert a + b < 0
