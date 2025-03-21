# Copyright 2025 Phi-Long Le. All rights reserved.
# Use of this source code is governed by a MIT license that can be
# found in the LICENSE file.

from pydantic import BaseModel, Field, FilePath

from crpatcher.config.util import CRPATCHER_STRICT_CONFIG


class ProgramContext(BaseModel):
    model_config = CRPATCHER_STRICT_CONFIG()
    config_file: FilePath = Field()
