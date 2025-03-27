from __future__ import annotations

from pathlib import Path

import pytest
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

from tests.base.pytest_cases import *


def _test_pathspec_with_pathlib():
    # Create a PathSpec with some test patterns
    patterns = ['file"', "temp.txt\0", "foo[0x07].log"]
    spec = PathSpec.from_lines(GitWildMatchPattern, patterns)

    # Test with various pathlib.Path objects (both POSIX and Windows style)
    test_paths = [
        Path("main.py"),
        Path("test_main.py"),
        Path("src/module/file.py"),
        Path("src/test_file.py"),
        Path("docs/readme.md"),
        Path("src\\module\\file.py"),  # Windows backslash
        Path("src\\test_file.py"),  # Windows backslash
        Path("C:\\Users\\name\\src\\file.py"),  # Windows absolute path
        Path("C:/Users/name/src/file.py"),  # Windows absolute path with forward slash
    ]

    # Convert paths to strings for match_files
    path_strings = [str(p) for p in test_paths]

    # Get matched files
    matched_files = set(spec.match_files(path_strings))

    print(matched_files)
    print(spec)

    # Verify results
    assert "main.py" in matched_files  # Should match *.py
    assert "test_main.py" not in matched_files  # Should be negated
    assert "src/module/file.py" in matched_files  # Should match src/**/*.py
    assert "src/test_file.py" not in matched_files  # Should be negated
    assert "docs/readme.md" not in matched_files  # Should not match any pattern
    assert (
        "src/module/file.py" in matched_files
    )  # Windows backslash should be normalized
    assert (
        "src/test_file.py" not in matched_files
    )  # Windows backslash should be normalized
    assert (
        "C:/Users/name/src/file.py" in matched_files
    )  # Windows absolute path should be normalized
    assert "C:/Users/name/src/file.py" in matched_files  # Forward slash should work too


@pytest_cases_parametrize(argnames="input", argvalues=[1, 2])
def case_1(input: int):
    return input


@pytest_cases_parametrize(argnames="input", argvalues=[3, 4])
def case_2(input: int):
    return input


@pytest_cases_parametrize_with_cases(argnames="input1", cases=case_1)
@pytest_cases_parametrize_with_cases(argnames="input2", cases=case_2)
def case_3(input1: int, input2: int):
    return input1 + input2


@pytest_cases_parametrize_with_cases(argnames="input", cases=case_3)
def test_case_3(input: int):
    assert input == 3 or input == 4
