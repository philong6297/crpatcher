from pathlib import Path

from pydantic import FilePath


def f(a: FilePath) -> None:
    pass


a = FilePath("a")
f(a)
