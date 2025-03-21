# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from __future__ import annotations

import json
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from crpatcher.config import CRPatcherConfig, PatchFileOption, PatchInfoOption
from tests.base.input_data import Input, InputType
from tests.unittests.config._test_crpatcher_config_fixtures import *
from tests.unittests.config.helper import (
    PatchFileOptionTestInput,
    PatchInfoOptionTestInput,
    RequestTestInput,
)


def CRPATCHER_CONFIG_DEFAULT() -> dict[str, Any]:
    return {
        "patch_file_opt": PatchFileOption(),
        "patchinfo_file_opt": PatchInfoOption(),
        "requests": [],
    }


class TestCRPatcherConfig:
    def test_direct_construction(
        self,
        patch_file_opt_fixt: Input[PatchFileOptionTestInput],
        patchinfo_file_opt_fixt: Input[PatchInfoOptionTestInput],
        requests_fixt: Input[list[RequestTestInput]],
    ) -> None:
        # Direct construction can only be tested with valid input data. Since any invalid input should raise error from the construction of each field member itself.
        if (
            patch_file_opt_fixt.type == InputType.INVALID
            or patchinfo_file_opt_fixt.type == InputType.INVALID
            or requests_fixt.type == InputType.INVALID
        ):
            return

        # Build kwargs dict only including non-DEFAULT fields
        kwargs: Dict[str, Any] = {}

        expected_config = CRPATCHER_CONFIG_DEFAULT()

        if patch_file_opt_fixt.type != InputType.DEFAULT:
            expected_config["patch_file_opt"] = (
                patch_file_opt_fixt.safe_data.build_patch_file_opt()
            )

            kwargs["patch_file_opt"] = expected_config["patch_file_opt"]

        if patchinfo_file_opt_fixt.type != InputType.DEFAULT:
            expected_config["patchinfo_file_opt"] = (
                patchinfo_file_opt_fixt.safe_data.build_patchinfo_file_opt()
            )
            kwargs["patchinfo_file_opt"] = expected_config["patchinfo_file_opt"]

        if requests_fixt.type != InputType.DEFAULT:
            expected_config["requests"] = [
                repository_data.build_patch_request()
                for repository_data in requests_fixt.safe_data
            ]
            kwargs["requests"] = expected_config["requests"]

        result = CRPatcherConfig(**kwargs)

        # For assertions, compare with value if not DEFAULT, otherwise use defaults
        assert result.patch_file_opt == expected_config["patch_file_opt"]
        assert result.patchinfo_file_opt == expected_config["patchinfo_file_opt"]
        assert result.requests == expected_config["requests"]

    def test_create_from_existing_config_file(
        self,
        crpatcher_base_dir_fixt: Path,
        patch_file_opt_fixt: Input[PatchFileOptionTestInput],
        patchinfo_file_opt_fixt: Input[PatchInfoOptionTestInput],
        requests_fixt: Input[list[RequestTestInput]],
    ) -> None:
        valid_config_file = _create_config_file(
            crpatcher_base_dir_fixt,
            patch_file_opt_fixt,
            patchinfo_file_opt_fixt,
            requests_fixt,
        )

        should_raise_error = (
            patch_file_opt_fixt.is_invalid_data
            or patchinfo_file_opt_fixt.is_invalid_data
            or requests_fixt.is_invalid_data
        )

        expected_context = (
            pytest.raises(ValidationError) if should_raise_error else nullcontext()
        )

        with expected_context:
            config = CRPatcherConfig.create_from_config_file(valid_config_file)

            if not should_raise_error:
                expected_config = CRPATCHER_CONFIG_DEFAULT()

                if patch_file_opt_fixt.type != InputType.DEFAULT:
                    expected_config["patch_file_opt"] = (
                        patch_file_opt_fixt.safe_data.build_patch_file_opt()
                    )

                if patchinfo_file_opt_fixt.type != InputType.DEFAULT:
                    expected_config["patchinfo_file_opt"] = (
                        patchinfo_file_opt_fixt.safe_data.build_patchinfo_file_opt()
                    )

                if requests_fixt.type != InputType.DEFAULT:
                    expected_config["requests"] = [
                        repository_data.build_patch_request()
                        for repository_data in requests_fixt.safe_data
                    ]

                assert config.patch_file_opt == expected_config["patch_file_opt"]
                assert (
                    config.patchinfo_file_opt == expected_config["patchinfo_file_opt"]
                )
                assert config.requests == expected_config["requests"]


def _create_config_file(
    base_dir: Path,
    patch_file_opt_test_input: Input[PatchFileOptionTestInput],
    patchinfo_file_opt_test_input: Input[PatchInfoOptionTestInput],
    requests_test_input: Input[list[RequestTestInput]],
) -> Path:
    # Construct the file name based on fixture states
    patch_file_opt_name = f"patch_file_opt_{patch_file_opt_test_input.type.name}"
    patchinfo_file_opt_name = (
        f"patchinfo_file_opt_{patchinfo_file_opt_test_input.type.name}"
    )
    requests_name = f"requests_{requests_test_input.type.name}"

    config_file_name = (
        f"{patch_file_opt_name}_{patchinfo_file_opt_name}_{requests_name}.json"
    )
    # Define the path for the config file
    config_file = base_dir.joinpath(config_file_name)

    if config_file.is_file():
        raise FileExistsError(
            f"Config file {config_file.as_posix()} already exists. It should be not at the time of running this test"
        )

    data: dict[str, Any] = {}

    if patch_file_opt_test_input.type != InputType.DEFAULT:
        data["patch_file_opt"] = patch_file_opt_test_input.safe_data._asdict()
    if patchinfo_file_opt_test_input.type != InputType.DEFAULT:
        data["patchinfo_file_opt"] = patchinfo_file_opt_test_input.safe_data._asdict()

    if requests_test_input.type != InputType.DEFAULT:
        data["requests"] = [
            # PatchRequest contains pathlib.Path, which is not serializable by default
            {
                "repo_dir": repo.repo_dir.safe_data.path.as_posix(),
                "patch_dir": repo.patch_dir.safe_data.path.as_posix(),
            }
            for repo in requests_test_input.safe_data
        ]

    with config_file.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    return config_file


# invalid file:
# - not exist TODO(longlp)
# - exist but not a file TODO(longlp)
# - exist but not a yaml format TODO(longlp)
# - exist but not a valid config DONE

# valid:
# - custom value DONE
# - default value DONE

#
#
#
