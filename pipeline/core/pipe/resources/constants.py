from __future__ import annotations

from typing import Generic, NamedTuple, TypeVar

from pipeline.handlers.condition_handler.resources.types import ConditionErrors

V = TypeVar('V')


class PipeResult(NamedTuple, Generic[V]):
    value: V

    condition_errors: ConditionErrors
    match_errors: ConditionErrors
