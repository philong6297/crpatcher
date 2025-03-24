from __future__ import annotations

from pathlib import Path

import pytest
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern


def test_pathspec_with_pathlib():
    # Create a PathSpec with some test patterns
    patterns = [
        "*.py",  # Matches any .py file at any level (1)
        "!**/test_*.py",  # Negate test files in all directories (2)
        "src/**/*.py",  # Match all Python files in src directory (3)
    ]
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

    expected_matches = [
        Path("main.py"),
        Path("src/module/file.py"),
        Path("src/test_file.py"),
        Path("src\\module\\file.py"),
        Path("src\\test_file.py"),
        Path("C:\\Users\\name\\src\\file.py"),
        Path("C:/Users/name/src/file.py"),
    ]

    # Get matched files
    matched_files = list(spec.match_files(test_paths))

    assert matched_files == expected_matches

    # Path("src/module/file.py") and Path("src\\module\\file.py") is the same, these duplicates should be reduced in result
    expected_set = set(expected_matches)
    actual_set = set(matched_files)
    assert expected_set == actual_set
