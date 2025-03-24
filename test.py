from __future__ import annotations

from pathlib import Path

import pytest
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern


def test_pathspec_with_pathlib():
    # Create a PathSpec with some test patterns
    patterns = [
        "*.py",
        "!test_*.py",  # Negate test files
        "src/**/*.py",  # Match all Python files in src directory
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

    # Convert paths to strings for match_files
    path_strings = [str(p) for p in test_paths]

    # Get matched files
    matched_files = set(spec.match_files(path_strings))

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
