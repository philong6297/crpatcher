# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

# WARN: this file is only meant to be included by test_crpatcher_config.py
# and should not be used as a standalone file.

import itertools
from pathlib import Path
from typing import Any, NamedTuple, Optional, cast

import pytest

from crpatcher.config import (
    PatchConfig,
    PatchInfoConfig,
    ProgramValidationContext,
    RepositoryConfig,
)
from tests.base.input_data import InputData, InputType


def CRPATCHER_CONFIG_DEFAULT() -> dict[str, Any]:
    return {
        "patch_config": PatchConfig(),
        "patch_info_config": PatchInfoConfig(),
        "repositories": [],
    }


class PatchConfigTestData(NamedTuple):
    ext: str
    encoding: str
    replacement_separator: str

    def build_patch_config(self) -> PatchConfig:
        return PatchConfig(
            encoding=self.encoding,
            replacement_separator=self.replacement_separator,
            ext=self.ext,
        )


class PatchInfoConfigTestData(NamedTuple):
    version: int
    ext: str
    encoding: str

    def build_patch_info_config(self) -> PatchInfoConfig:
        return PatchInfoConfig(
            version=self.version,
            encoding=self.encoding,
            ext=self.ext,
        )


class PathTestData(NamedTuple):
    path: Path
    base_dir: Path
    use_absolute_path: bool


class RepositoryTestData(NamedTuple):
    repo_dir: InputData[PathTestData]
    patch_dir: InputData[PathTestData]
    program_context: InputData[Optional[ProgramValidationContext]]

    @property
    def is_valid(self) -> bool:
        # there is no default program_context, repo_dir or patch_dir we always need to create it
        if (
            self.repo_dir.type != InputType.CUSTOM
            or self.patch_dir.type != InputType.CUSTOM
            or self.program_context.type != InputType.CUSTOM
        ):
            return False

        if self.construction_needs_program_context:
            # program_context is required
            return self.program_context.safe_value is not None

        return True

    @property
    def construction_needs_program_context(self) -> bool:
        # both directories are absolute paths, no need to use program_context
        return not (
            self.repo_dir.safe_value.use_absolute_path
            and self.patch_dir.safe_value.use_absolute_path
        )

    def build_repository_config(self) -> RepositoryConfig:
        if not self.is_valid:
            raise ValueError(
                "RepositoryTestData is invalid. Cannot build RepositoryConfig."
            )

        repo_dir_data: PathTestData = self.repo_dir.safe_value
        patch_dir_data: PathTestData = self.patch_dir.safe_value

        if self.construction_needs_program_context:
            return RepositoryConfig.create_with_context(
                repo_dir=repo_dir_data.path,
                patch_dir=patch_dir_data.path,
                program_context=self.program_context.safe_value,
            )

        return RepositoryConfig(
            repo_dir=repo_dir_data.path,
            patch_dir=patch_dir_data.path,
        )


def _generate_fixt_params_and_ids(fixture_name: str) -> dict[str, Any]:
    params, ids = zip(*[(type, f"{fixture_name}_{type.name}") for type in InputType])
    return {
        "params": list(params),
        "ids": list(ids),
    }


def _make_folder_input_data(
    base_dir: Path,
    existing_empty_dir: Path,
    non_existent_dir: Path,
    use_valid_path: bool,
    use_absolute_path: bool,
) -> InputData[PathTestData]:
    path_value = existing_empty_dir if use_valid_path else non_existent_dir

    return InputData(
        value=PathTestData(
            path=(
                path_value if use_absolute_path else path_value.relative_to(base_dir)
            ),
            base_dir=base_dir,
            use_absolute_path=use_absolute_path,
        ),
        type=InputType.CUSTOM if use_valid_path else InputType.INVALID,
    )


@pytest.fixture(scope="class")
def repository_input_datas_fixt(
    crpatcher_existing_empty_file: Path,
    crpatcher_test_base_dir: Path,
    crpatcher_existing_empty_dir: Path,
    crpatcher_non_existent_dir: Path,
) -> list[RepositoryTestData]:
    program_context_datas: list[InputData[Optional[ProgramValidationContext]]] = [
        InputData(
            value=ProgramValidationContext(config_file=crpatcher_existing_empty_file),
            type=InputType.CUSTOM,
        ),  # build validation context from existing file
        InputData(value=None, type=InputType.CUSTOM),  # no validation context
    ]

    PATH_CONDITIONS = itertools.product(
        [
            True,  # exist path
            False,  # non-exist path
        ],
        [
            True,  # use absolute path
            False,  # use relative path
        ],
    )

    repo_dir_datas = [
        _make_folder_input_data(
            base_dir=crpatcher_test_base_dir,
            existing_empty_dir=crpatcher_existing_empty_dir,
            non_existent_dir=crpatcher_non_existent_dir,
            use_valid_path=use_valid_path,
            use_absolute_path=use_absolute_path,
        )
        for use_valid_path, use_absolute_path in PATH_CONDITIONS
    ]

    # TODO(longlp): Why not work
    # patch_dir_datas = [
    #     _make_folder_input_data(
    #         base_dir=crpatcher_test_base_dir,
    #         existing_empty_dir=crpatcher_existing_empty_dir,
    #         non_existent_dir=crpatcher_non_existent_dir,
    #         use_valid_path=use_valid_path,
    #         use_absolute_path=use_absolute_path,
    #     )
    #     for use_valid_path, use_absolute_path in PATH_CONDITIONS
    # ]
    patch_dir_datas = repo_dir_datas.copy()

    return [
        RepositoryTestData(
            repo_dir=repo_dir_data,
            patch_dir=patch_dir_data,
            program_context=program_context_data,
        )
        for repo_dir_data, patch_dir_data, program_context_data in itertools.product(
            repo_dir_datas, patch_dir_datas, program_context_datas
        )
    ]


@pytest.fixture(
    scope="class",
    **_generate_fixt_params_and_ids("repositories"),
)
def repositories_fixt(
    request: pytest.FixtureRequest,
    repository_input_datas_fixt: list[RepositoryTestData],
) -> InputData[list[RepositoryTestData]]:
    if request.param == InputType.DEFAULT:
        return InputData()

    valid_repositories: list[RepositoryTestData] = []
    invalid_repositories: list[RepositoryTestData] = []

    for data in repository_input_datas_fixt:
        if data.is_valid:
            valid_repositories.append(data)
        else:
            invalid_repositories.append(data)

    if request.param == InputType.CUSTOM:
        return InputData(
            value=valid_repositories,
            type=InputType.CUSTOM,
        )

    return InputData(
        value=invalid_repositories,
        type=InputType.INVALID,
    )


@pytest.fixture(
    scope="class",
    **_generate_fixt_params_and_ids("patch_config"),
)
def patch_config_fixt(request: pytest.FixtureRequest) -> InputData[PatchConfigTestData]:
    match cast(InputType, request.param):
        case InputType.DEFAULT:
            return InputData()
        case InputType.CUSTOM:
            return InputData(
                value=PatchConfigTestData(
                    ext="custom_ext",
                    encoding="ascii",
                    replacement_separator="custom-replacement-separator",
                ),
                type=InputType.CUSTOM,
            )
        case InputType.INVALID:
            return InputData(
                value=PatchConfigTestData(
                    ext="invalid-ext",
                    encoding="invalid-encoding",
                    replacement_separator="invalid+sep",
                ),
                type=InputType.INVALID,
            )


@pytest.fixture(
    scope="class",
    **_generate_fixt_params_and_ids("patch_info_config"),
)
def patch_info_config_fixt(
    request: pytest.FixtureRequest,
) -> InputData[PatchInfoConfigTestData]:
    match cast(InputType, request.param):
        case InputType.DEFAULT:
            return InputData()
        case InputType.CUSTOM:
            return InputData(
                value=PatchInfoConfigTestData(
                    version=2,
                    ext="custom_ext",
                    encoding="ascii",
                ),
                type=InputType.CUSTOM,
            )
        case InputType.INVALID:
            return InputData(
                value=PatchInfoConfigTestData(
                    version=-1,
                    ext="invalid$ext",
                    encoding="invalid_encoding",
                ),
                type=InputType.INVALID,
            )
