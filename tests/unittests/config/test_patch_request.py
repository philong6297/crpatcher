# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

from contextlib import nullcontext
from typing import Any

import pytest
from pydantic import ValidationError

from crpatcher.config import PatchRequest
from tests.unittests.config.helper import InputType, RequestTestInput


class TestPatchRequest:
    def test_direct_construction(
        self,
        crpatcher_all_request_test_inputs_fixt: list[RequestTestInput],
    ) -> None:
        # Test repository config construction behavior.
        # When using absolute paths (needs_context=False), direct constructor should work.
        # Otherwise, it should raise ValidationError.

        for test_case in crpatcher_all_request_test_inputs_fixt:
            should_raise_error = not test_case.is_valid

            if not test_case.construction_needs_program_context:
                with (
                    pytest.raises(ValidationError)
                    if should_raise_error
                    else nullcontext()
                ):
                    other_args: dict[str, Any] = {}
                    if test_case.keep_patch_files.type != InputType.DEFAULT:
                        other_args["keep_patch_files"] = (
                            test_case.keep_patch_files.safe_data
                        )
                    if test_case.ignore_patterns.type != InputType.DEFAULT:
                        other_args["ignore_patterns"] = (
                            test_case.ignore_patterns.safe_data
                        )

                    config = PatchRequest(
                        repo_dir=test_case.repo_dir.safe_data.path,
                        patch_dir=test_case.patch_dir.safe_data.path,
                        **other_args,
                    )

                    if not should_raise_error:
                        # Verify paths are absolute and exist
                        assert config.repo_dir.is_absolute()
                        assert config.patch_dir.is_absolute()
                        assert config.repo_dir.is_dir()
                        assert config.patch_dir.is_dir()

                        # Verify paths are resolved correctly.
                        # Since we are using direct construction, the paths must be all absolute and exactly the same as input
                        assert config.repo_dir == test_case.repo_dir.safe_data.path
                        assert config.patch_dir == test_case.patch_dir.safe_data.path

                        if test_case.keep_patch_files.type != InputType.DEFAULT:
                            assert (
                                config.keep_patch_files
                                == test_case.keep_patch_files.safe_data
                            )
                        else:
                            assert config.keep_patch_files == []

                        if test_case.ignore_patterns.type != InputType.DEFAULT:
                            assert (
                                config.ignore_patterns
                                == test_case.ignore_patterns.safe_data
                            )
                        else:
                            assert config.ignore_patterns == []

    def test_construction_with_program_context(
        self,
        crpatcher_all_request_test_inputs_fixt: list[RequestTestInput],
    ) -> None:
        # Test with PatchRequest.create_with_context.
        #
        # Any invalid path (use_valid_path=False) should raise ValidationError.
        # For relative paths, validation context must be present.

        for test_case in crpatcher_all_request_test_inputs_fixt:
            should_raise_error = not test_case.is_valid

            with (
                pytest.raises(ValidationError) if should_raise_error else nullcontext()
            ):
                other_args: dict[str, Any] = {}
                if test_case.keep_patch_files.type != InputType.DEFAULT:
                    other_args["keep_patch_files"] = (
                        test_case.keep_patch_files.safe_data
                    )
                if test_case.ignore_patterns.type != InputType.DEFAULT:
                    other_args["ignore_patterns"] = test_case.ignore_patterns.safe_data
                config = PatchRequest.create_with_context(
                    program_context=test_case.program_context.safe_data,
                    repo_dir=test_case.repo_dir.safe_data.path,
                    patch_dir=test_case.patch_dir.safe_data.path,
                    **other_args,
                )

                if not should_raise_error:
                    # Verify paths are absolute and exist
                    assert config.repo_dir.is_absolute()
                    assert config.patch_dir.is_absolute()
                    assert config.repo_dir.is_dir()
                    assert config.patch_dir.is_dir()

                    # Verify relative paths are resolved correctly

                    expected_repo_dir = (
                        test_case.repo_dir.safe_data.path
                        if test_case.repo_dir.safe_data.use_absolute_path
                        else test_case.repo_dir.safe_data.base_dir.joinpath(
                            test_case.repo_dir.safe_data.path
                        )
                    )
                    expected_patch_dir = (
                        test_case.patch_dir.safe_data.path
                        if test_case.patch_dir.safe_data.use_absolute_path
                        else test_case.patch_dir.safe_data.base_dir.joinpath(
                            test_case.patch_dir.safe_data.path
                        )
                    )

                    assert config.repo_dir == expected_repo_dir
                    assert config.patch_dir == expected_patch_dir
                    assert config.patch_dir == expected_patch_dir

                    if test_case.keep_patch_files.type != InputType.DEFAULT:
                        assert (
                            config.keep_patch_files
                            == test_case.keep_patch_files.safe_data
                        )
                    else:
                        assert config.keep_patch_files == []

                    if test_case.ignore_patterns.type != InputType.DEFAULT:
                        assert (
                            config.ignore_patterns
                            == test_case.ignore_patterns.safe_data
                        )
                    else:
                        assert config.ignore_patterns == []
