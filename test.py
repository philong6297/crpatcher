from typing import TypeAlias, TypeVar, Union, get_args

T = TypeVar("T")

# Automatically exclude None from the type
NonNullable: TypeAlias = lambda T: Union[
    tuple(t for t in get_args(T) if t is not type(None))
]

# Example Usage
TypeA = Union[str, None]
RefinedA = NonNullable(TypeA)  # Should resolve to `str`

print(RefinedA)  # ✅ Output: <class 'str'>
