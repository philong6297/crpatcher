import logging
import os

from crpatcher.config import CrPatcherConfig
from crpatcher.patch_gen import GitPatchFileGenerator

__all__ = ["command_generate_patches"]

_logger = logging.getLogger(__name__)


def command_generate_patches(config: CrPatcherConfig) -> None:
    for request in config.requests:
        _logger.info(
            f"Generating patches for {request.repo_dir.as_posix()}{os.linesep}"
            f"Storing in {request.patch_dir.as_posix()}"
        )
        generator = GitPatchFileGenerator(
            patch_request=request,
            patch_file_extension=config.PATCH_FILE_EXTENSION,
            patch_file_encoding=config.PATCH_FILE_ENCODING,
            patch_file_name_separator=config.PATCH_FILE_NAME_SEPARATOR,
        )
        generator.update_patches()

    _logger.info("Done.")
