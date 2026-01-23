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
    3. Setup: Executes setup (transform) handlers (e.g. Strip) to modify the value. Only the
       value type is validated prior to this stage.
    4. Conditions: Runs a set of condition handlers. If any fail, errors are collected, and processing
       may stop if `BREAK_PIPE_LOOP_ON_ERROR` flag is set.
    5. Matches: Only if no condition errors occurred, match handlers are executed. These are typically
       regex-based checks.
    6. Transform: Only if no match errors occurred, transform handlers are executed to modify the value.

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
        setup: Optional[PipeTransform] = None,
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
            setup (Optional[PipeTransform]): A dictionary of transform handlers and their arguments.
                Used for data setup (e.g. Strip). Use with caution. Setup runs after type validation, but
                before conditions, matches, and transform handlers. Only the value type is
                validated at the time of setup execution.
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

        self.setup: Optional[PipeTransform] = setup

        self.conditions: Optional[PipeConditions] = conditions
        self.matches: Optional[PipeMatches] = matches
        self.transform: Optional[PipeTransform] = transform

        self.optional: Optional[bool] = optional

        self.context: Optional[PipeContext] = context
        self.metadata: Optional[PipeMetadata] = metadata

        self._condition_errors: ConditionErrors = []
        self._match_errors: ConditionErrors = []

    def run(self) -> PipeResult:
        """
        Executes the pipe processing logic.

        The method orchestrates the execution flow by delegating to specialized helper methods:
        1. Checks if validation should be skipped (optional pipe with falsy value)
        2. Validates the value type
        3. Processes setup handlers (if any)
        4. Processes condition handlers
        5. Processes match handlers (only if no condition errors)
        6. Processes transform handlers (only if no condition or match errors)

        Note that transformations are ONLY applied if all validations (Conditions and Matches) pass.
        This provides a safe way to transform data, ensuring it is valid first.

        Returns:
            PipeResult[V]: The result containing the processed value (or original value if errors occurred)
            and lists of any condition or match errors.
        """
        if self._should_skip_validation():
            return self._construct_result()

        if not self._is_value_type_correct():
            return self._construct_result()

        self._process_setup()

        self._process_conditions()
        self._process_matches()
        self._process_transform()

        return self._construct_result()

    def _construct_result(self) -> PipeResult:
        """
        Constructs and returns the final PipeResult.
        
        If the pipe is marked as optional and the value is falsy, 
        the result value is set to None.

        Returns:
            PipeResult: A result object containing the current value (or None 
            if optional and empty) and any accumulated condition or match errors.
        """
        value: V | None = None if self.optional and not bool(
            self.value
        ) else self.value

        return PipeResult(
            value=value,
            condition_errors=self._condition_errors,
            match_errors=self._match_errors
        )

    def _should_skip_validation(self) -> bool:
        """
        Determines whether validation should be skipped for this pipe.

        Validation is skipped only if the pipe is marked as optional and the value is falsy
        (e.g., None, empty string, 0, False).

        Returns:
            bool: True if validation should be skipped, False otherwise.
        """
        if not self.optional:
            return False

        return not bool(self.value)

    def _is_value_type_correct(self) -> bool:
        """
        Validates that the value matches the expected type.

        Uses the `Condition.ValueType` handler to check type correctness. If the type
        is incorrect, an error is appended to the condition errors list.

        Returns:
            bool: True if the value type is correct, False otherwise.
        """
        if (error := self.Condition.ValueType(self.value, self.type).handle()):
            self._condition_errors.append(error)

        return not error

    def _process_setup(self) -> None:
        """
        Processes setup transform handlers to prepare the value for validation.

        Setup handlers are executed after type validation but before conditions, matches,
        and transform handlers. They are typically used for data normalization (e.g., Strip).
        Each handler modifies the value in place.

        Note:
            Setup handlers run even if subsequent validations might fail. Use with caution.
        """
        if not self.setup:
            return

        for handler, argument in self.setup.items():
            self.value = handler(
                value=self.value, argument=argument, context=self.context
            ).handle()

    def _process_conditions(self) -> None:
        """
        Processes condition handlers to validate the value.

        Iterates through all condition handlers and executes them. If a handler returns an error,
        it is appended to the condition errors list. If a handler has the `BREAK_PIPE_LOOP_ON_ERROR`
        flag set, the loop terminates immediately upon encountering an error.

        Note:
            Condition errors prevent match and transform handlers from executing.
        """
        if not self.conditions:
            return

        for handler, argument in self.conditions.items():
            handler = handler(
                value=self.value, argument=argument, context=self.context
            )

            if (error := handler.handle()):
                self._condition_errors.append(error)

                if ConditionFlag.BREAK_PIPE_LOOP_ON_ERROR in handler.FLAGS:
                    break

    def _process_matches(self) -> None:
        """
        Processes match handlers to perform pattern-based validation.

        Match handlers are only executed if no condition errors occurred. Typically used for
        regex-based validation (e.g., Email, URL patterns). The loop terminates immediately
        upon the first match error.

        Note:
            This method is skipped if any condition errors exist. Match errors prevent
            transform handlers from executing.
        """
        if not self.matches or len(self._condition_errors) != 0:
            return

        for handler, argument in self.matches.items():
            handler = handler(
                value=self.value, argument=argument, context=self.context
            )

            if (error := handler.handle()):
                self._match_errors.append(error)

                break

    def _process_transform(self) -> None:
        """
        Processes transform handlers to modify the value.

        Transform handlers are only executed if no condition or match errors occurred.
        This ensures that transformations are only applied to valid data. Each handler
        modifies the value in place.

        Note:
            This method is skipped if any condition or match errors exist, ensuring
            transformations are only applied to validated data.
        """
        if not self.transform or len(self._condition_errors) != 0 or\
                                 len(self._match_errors) != 0:
            return

        for handler, argument in self.transform.items():
            self.value = handler(
                value=self.value, argument=argument, context=self.context
            ).handle()
