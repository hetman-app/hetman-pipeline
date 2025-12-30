from __future__ import annotations

from functools import partial
from typing import Any, Type

from pipeline.handlers.condition_handler.condition_handler import \
    ConditionHandler
from pipeline.handlers.match_handler.match_handler import MatchHandler
from pipeline.handlers.transform_handler.transform_handler import \
    TransformHandler

PipeConditions = dict[Type[ConditionHandler] | partial[ConditionHandler], Any]
PipeMatches = dict[Type[MatchHandler] | partial[MatchHandler], Any]
PipeTransform = dict[Type[TransformHandler] | partial[TransformHandler], Any]

PipeContext = dict[str, Any]
PipeMetadata = dict[str, Any]
