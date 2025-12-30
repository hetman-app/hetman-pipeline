from typing import ClassVar, Generic, Optional, Type, TypeVar

from pipeline.core.pipe.resources.constants import PipeResult
from pipeline.core.pipe.resources.types import (
    PipeConditions, PipeContext, PipeMatches, PipeMetadata, PipeTransform
)
from pipeline.handlers.condition_handler.condition import Condition
from pipeline.handlers.condition_handler.resources.constants import \
    ConditionFlag
from pipeline.handlers.condition_handler.resources.types import ConditionErrors
from pipeline.handlers.match_handler.match import Match
from pipeline.handlers.transform_handler.transform import Transform

V = TypeVar("V")
T = TypeVar("T", bound=type)


class Pipe(Generic[V, T]):
    """
    A Pipe processes a single value through validation, matching, and transformation steps.

    The execution flow is strict:
    1. Optional Check: If the pipe is optional and the value is falsy, it returns early.
    2. Type Validation: Checks if the value matches the expected type (via `Condition.ValueType`).
    3. Conditions: Runs a set of condition handlers. If any fail, errors are collected, and processing
       may stop if `BREAK_PIPE_LOOP_ON_ERROR` flag is set.
    4. Matches: Only if no condition errors occurred, match handlers are executed. These are typically
       regex-based checks.
    5. Transform: Only if no match errors occurred, transform handlers are executed to modify the value.

    Attributes:
        Condition (Type[Condition]): The condition handler class registry.
        Match (Type[Match]): The match handler class registry.
        Transform (Type[Transform]): The transform handler class registry.
    """
    Condition: ClassVar[Type[Condition]] = Condition
    Match: ClassVar[Type[Match]] = Match
    Transform: ClassVar[Type[Transform]] = Transform

    def __init__(
        self,
        value: V,
        type: T,
        conditions: Optional[PipeConditions] = None,
        matches: Optional[PipeMatches] = None,
        transform: Optional[PipeTransform] = None,
        optional: Optional[bool] = None,
        context: Optional[PipeContext] = None,
        metadata: Optional[PipeMetadata] = None
    ) -> None:
        """
        Initializes the Pipe with a value, type, and processing configurations.

        Args:
            value (V): The value to process.
            type (T): The expected type of the value (e.g., `str`, `int`).
            conditions (Optional[PipeConditions]): A dictionary of condition handlers and their arguments.
                Used for logical validation (e.g., `MinLength`, `Equal`).
            matches (Optional[PipeMatches]): A dictionary of match handlers and their arguments.
                Used for pattern matching (e.g., `Email`, `Regex`).
            transform (Optional[PipeTransform]): A dictionary of transform handlers and their arguments.
                Used for data modification (e.g., `Strip`, `Capitalize`).
            optional (Optional[bool]): If True, the pipe is skipped if the value is falsy.
            context (Optional[PipeContext]): Additional context for the handlers, typically the
                entire data dictionary being processed.
            metadata (Optional[PipeMetadata]): Metadata about the pipe execution.
        """
        self.value: V = value

        self.type: T = type

        self.conditions: Optional[PipeConditions] = conditions
        self.matches: Optional[PipeMatches] = matches
        self.transform: Optional[PipeTransform] = transform

        self.optional: Optional[bool] = optional

        self.context: Optional[PipeContext] = context
        self.metadata: Optional[PipeMetadata] = metadata

        self._condition_errors: ConditionErrors = []
        self._match_errors: ConditionErrors = []

    def run(self) -> PipeResult[V]:
        """
        Executes the pipe processing logic.

        The method strictly follows the defined order of operations. Note that
        Transformations are ONLY applied if all validations (Conditions and Matches) pass.
        This provides a safe way to transform data, ensuring it is valid first.

        Returns:
            PipeResult[V]: The result containing the processed value (or original value if errors occurred)
            and lists of any condition or match errors.
        """
        if self.optional and (bool(self.value) is False):
            return PipeResult(
                value=self.value, condition_errors=[], match_errors=[]
            )

        if (error := self.Condition.ValueType(self.value, self.type).handle()):
            return PipeResult(
                value=self.value, condition_errors=[error], match_errors=[]
            )

        if self.conditions:
            for handler, argument in self.conditions.items():
                handler = handler(
                    value=self.value, argument=argument, context=self.context
                )

                if (error := handler.handle()):
                    self._condition_errors.append(error)

                    if ConditionFlag.BREAK_PIPE_LOOP_ON_ERROR in handler.FLAGS:
                        break

        if len(self._condition_errors) == 0:
            if self.matches:
                for handler, argument in self.matches.items():
                    handler = handler(
                        value=self.value,
                        argument=argument,
                        context=self.context
                    )

                    if (error := handler.handle()):
                        self._match_errors.append(error)

                        break

            if self.transform and len(self._match_errors) == 0:
                for handler, argument in self.transform.items():
                    self.value = handler(
                        value=self.value,
                        argument=argument,
                        context=self.context
                    ).handle()

        return PipeResult(
            value=self.value,
            condition_errors=self._condition_errors,
            match_errors=self._match_errors
        )
