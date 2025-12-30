from typing import Any, Callable, NotRequired, Protocol, TypedDict

from pipeline.core.pipe.resources.types import (
    PipeConditions, PipeMatches, PipeMetadata, PipeTransform
)
from pipeline.core.pipeline.resources.constants import PipelineHook
from pipeline.handlers.condition_handler.resources.types import ConditionErrors


class PipelinePipeConfig(TypedDict):
    type: type

    conditions: NotRequired[PipeConditions]
    matches: NotRequired[PipeMatches]
    transform: NotRequired[PipeTransform]

    optional: NotRequired[bool]

    metadata: NotRequired[PipeMetadata]


PipelineErrors = dict[str, ConditionErrors]
PipelineHookFunc = Callable[[PipelineHook], None]
PipelineHandleErrorsFunc = Callable[[PipelineErrors], None]


class PipelineHookValue(Protocol):
    @property
    def get(self) -> Any:
        ...

    def set(self, new_value: Any) -> Any:
        ...
