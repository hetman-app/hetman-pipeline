from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    from pipeline.core.pipeline.resources.types import (
        PipelineErrors, PipelineHookValue, PipelinePipeConfig
    )


@dataclass
class PipelineHook:
    field: Any

    value: PipelineHookValue

    is_valid: bool | None

    pipe_config: PipelinePipeConfig


class PipelineResult(NamedTuple):
    errors: PipelineErrors | None

    processed_data: dict | None
