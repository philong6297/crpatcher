# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

# pyright: reportUnknownVariableType=false

from typing import Any, Callable

from decopatch import DECORATED as _LIB_DECORATED
from decopatch import function_decorator as _function_decorator
from pytest_cases import AUTO as _LIB_AUTO
from pytest_cases import fixture as _lib_fixture
from pytest_cases import parametrize as _lib_parametrize
from pytest_cases import parametrize_with_cases as _lib_parametrize_with_cases

__all__ = [
    "pytest_cases_parametrize",
    "pytest_cases_fixture",
    "pytest_cases_parametrize_with_cases",
]


_IDGEN = object()


def pytest_cases_parametrize(
    argnames: Any = None,
    argvalues: Any = None,
    indirect: Any = False,
    ids: Any = None,
    idstyle: Any = None,
    idgen: Any = _IDGEN,
    auto_refs: Any = True,
    scope: Any = None,
    hook: Any = None,
    debug: Any = False,
    **args: Any,
) -> Callable[[Any], Any]:
    return _lib_parametrize(
        argnames=argnames,
        argvalues=argvalues,
        indirect=indirect,
        ids=ids,
        idstyle=idstyle,
        idgen=idgen,
        auto_refs=auto_refs,
        scope=scope,
        hook=hook,
        debug=debug,
        **args,
    )


@_function_decorator
def pytest_cases_fixture(
    scope: Any = "function",
    autouse: Any = False,
    name: Any = None,
    unpack_into: Any = None,
    hook: Any = None,
    fixture_func: Any = _LIB_DECORATED,
    **kwargs: Any,
) -> Callable[[Any], Any]:
    return _lib_fixture(
        scope=scope,
        autouse=autouse,
        name=name,
        unpack_into=unpack_into,
        hook=hook,
        fixture_func=fixture_func,
        **kwargs,
    )


CASE_PREFIX_FUN = "case_"


def pytest_cases_parametrize_with_cases(
    argnames: Any,
    cases: Any = _LIB_AUTO,
    prefix: Any = CASE_PREFIX_FUN,
    glob: Any = None,
    has_tag: Any = None,
    filter: Any = None,
    ids: Any = None,
    idstyle: Any = None,
    debug: Any = False,
    scope: Any = "function",
    import_fixtures: Any = False,
) -> Callable[[Any], Any]:
    return _lib_parametrize_with_cases(
        argnames=argnames,
        cases=cases,
        prefix=prefix,
        glob=glob,
        has_tag=has_tag,
        filter=filter,
        ids=ids,
        idstyle=idstyle,
        debug=debug,
        scope=scope,
        import_fixtures=import_fixtures,
    )
