from __future__ import annotations

import re
from abc import ABC, abstractmethod
from functools import cached_property
from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Generic, Iterable, Optional,
    TypeVar, get_args
)

from pipeline.handlers.base_handler.resources.constants import (
    Flag, HandlerExpectedTypes, HandlerMode
)
from pipeline.handlers.base_handler.resources.exceptions import (
    HandlerException, HandlerInvalidArgumentType,
    HandlerInvalidPreferredValueType, HandlerInvalidValueType,
    HandlerModeMissingContextValue, HandlerModeUnsupported
)

if TYPE_CHECKING:
    from pipeline.core.pipe.resources.types import PipeContext, PipeMetadata

V = TypeVar('V')
A = TypeVar('A')


class BaseHandler(ABC, Generic[V, A]):
    """
    Abstract base class for all handlers in the pipeline.

    Handlers are the building blocks of the pipeline, responsible for processing values
    (validation, matching, transformation) based on provided arguments and context.
    They support different modes of operation to handle single values, items in a collection,
    or values dependent on other context fields.

    Attributes:
        FLAGS (ClassVar[tuple[Flag, ...]]): Flags acting as settings for the handler.
            Example: `ConditionFlag.BREAK_PIPE_LOOP_ON_ERROR` stops processing if the handler fails.
        SUPPORT (ClassVar[tuple[HandlerMode, ...]]): Supported handler modes.
            - `HandlerMode.ROOT`: The handler processes the value directly.
            - `HandlerMode.ITEM`: The handler processes each item in a list/dict.
            - `HandlerMode.CONTEXT`: The handler uses another field from the context as an argument.
        CONTEXT_ARGUMENT_BUILDER (ClassVar[Optional[Callable]]): Helper to build arguments from context.
            Used in CONTEXT mode to transform the context value before using it as an argument.
    """
    FLAGS: ClassVar[tuple[Flag, ...]] = tuple()

    SUPPORT: ClassVar[tuple[HandlerMode, ...]] = tuple()

    CONTEXT_ARGUMENT_BUILDER: ClassVar[Optional[Callable[['BaseHandler', Any],
                                                         Any]]] = None

    def __init__(
        self,
        value: V,
        argument: A,
        context: Optional[PipeContext] = None,
        metadata: Optional[PipeMetadata] = None,
        _mode: HandlerMode = HandlerMode.ROOT,
        _item_use_key: Optional[bool] = False,
        _preferred_value_type: Optional[type] = None
    ) -> None:
        """
        Initializes the BaseHandler.

        Args:
            value (V): The value to process.
            argument (A): The argument for the handler.
            context (Optional[PipeContext]): Additional context for the handler.
            metadata (Optional[PipeMetadata]): Metadata about the pipe execution.
            _mode (HandlerMode): The mode in which the handler is operating.
            _item_use_key (Optional[bool]): If True and in ITEM mode, the handler operates on the
                key of a dictionary item instead of the value.
            _preferred_value_type (Optional[type]): Specific type to prefer/enforce during type validation.
        """
        self.value: V = value
        self.argument: A = argument

        self.input_value: V = value
        self.input_argument: A = argument

        self.context: PipeContext = context or {}
        self.metadata: PipeMetadata = metadata or {}

        self._mode: HandlerMode = _mode

        self._item_index: Optional[int | str] = None
        self._item_use_key: Optional[bool] = _item_use_key

        self._preferred_value_type: Optional[type] = _preferred_value_type

        self._prepare_and_validate_handler()

    def handle(self) -> Any:
        """
        Executes the handler logic based on the current mode.

        It delegates to `_handle()` for ROOT and CONTEXT modes, and `_handle_item_mode()`
        for ITEM mode.

        Returns:
            Any: The result of the handling operation. The return type depends on the specific
            handler implementation (e.g., specific error type, boolean, or transformed value).

        Raises:
            HandlerException: If the handler mode is invalid.
        """
        if self._mode in (HandlerMode.ROOT, HandlerMode.CONTEXT):
            return self._handle()
        elif self._mode == HandlerMode.ITEM:
            return self._handle_item_mode()
        else:
            raise HandlerException("Invalid handler mode.")

    def _prepare_and_validate_handler(self) -> None:
        """
        Prepares the handler for the current mode and validates input types.

        This methods checks if the requested mode is supported, perpares the handler argument
        (especially for CONTEXT mode), and validates that value and argument types match
        expectations (generics).

        Raises:
            HandlerModeUnsupported: If the current mode is not supported by the handler.
        """
        if self._mode not in self.SUPPORT:
            raise HandlerModeUnsupported(handler_mode=self._mode)

        self._prepare_handler_for_mode()
        self._validate_type_if_possible()

    def _prepare_handler_for_mode(self) -> None:
        """
        Performs specific preparation steps based on the handler mode.
        
        For CONTEXT mode, it retrieves the argument from the context using the provided
        argument name (stored in `self.argument`). It also handles optional argument transformation
        via `CONTEXT_ARGUMENT_BUILDER`.
        """
        match self._mode:
            case HandlerMode.CONTEXT:
                context_value: Any = self.context.get(str(self.argument), None)

                if context_value is None:
                    raise HandlerModeMissingContextValue(
                        argument=str(self.argument)
                    )

                self.argument = self.CONTEXT_ARGUMENT_BUILDER(
                    context_value
                ) if self.CONTEXT_ARGUMENT_BUILDER else context_value

    def _is_valid_type(
        self, value: Any, expected_type: type | tuple[type, ...]
    ) -> bool:
        """
        Checks if a value matches the expected type(s).

        Args:
            value (Any): The value to check.
            expected_type (type | tuple[type, ...]): The expected type or tuple of types.

        Returns:
            bool: True if the value matches the expected type, False otherwise.
        """
        if isinstance(expected_type, Iterable):
            if Any in expected_type:
                return True

            return isinstance(value, expected_type)

        return expected_type == Any or isinstance(value, expected_type)

    def _validate_type_if_possible(self) -> None:
        """
        Validates the types of the input value and argument against the class generics.

        This ensures type safety at runtime, verifying that the handler is being applied
        to compatible data.

        Value type is only verified for ROOT and CONTEXT modes.For ITEM mode, the handler
        must implement its own logic.

        Raises:
            HandlerInvalidValueType: If the value type is invalid.
            HandlerInvalidArgumentType: If the argument type is invalid.
        """
        if self._mode in (HandlerMode.ROOT, HandlerMode.CONTEXT):
            if not self._is_valid_type(self.value, self._expected_value_type):
                raise HandlerInvalidValueType(handler=self)

        if not self._is_valid_type(self.argument, self._expected_argument_type):
            raise HandlerInvalidArgumentType(handler=self)

    @abstractmethod
    def _handle(self) -> Any:
        """
        Abstract method to implement the main handling logic.
        """
        ...

    @abstractmethod
    def _handle_item_mode(self) -> Any:
        """
        Abstract method to implement the handling logic for ITEM mode.
        """
        ...

    @property
    def id(self) -> str:
        """
        Returns a unique identifier for the handler based on its class name.

        Returns:
            str: The snake_case identifier of the handler (e.g., 'MaxLength' -> 'max_length').
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.__class__.__name__)

        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @cached_property
    def _expected_types(self) -> HandlerExpectedTypes:
        """
        Determines the expected value and argument types from the generic type arguments.

        This introspects the class definition to find the concrete types provided for
        `BaseHandler[V, A]`.

        Returns:
            HandlerExpectedTypes: Named tuple containing expected value and argument types.

        Raises:
            TypeError: If the class does not inherit from BaseHandler correctly or has incorrect generic arguments.
            HandlerInvalidPreferredValueType: If the preferred value type is invalid.
        """
        orig_bases: list[Any] = getattr(self, "__orig_bases__", [])

        if len(orig_bases) != 1:
            raise TypeError(
                "Handler subclass must inherit from a generic base class (e.g. BaseHandler[V, A])."
            )

        generic_args: tuple[Any, ...] = get_args(orig_bases[0])

        if len(generic_args) != 2:
            raise TypeError(
                f"Expected 2 generic arguments on base class, found {len(generic_args)}."
            )

        def _unpack_generic_args(arg: Any) -> Any:
            generic_args = get_args(arg)

            if generic_args:
                return tuple(
                    _unpack_generic_args(sub_arg) for sub_arg in generic_args
                )

            return arg

        expected_value_type: tuple[type, ...] | type = _unpack_generic_args(
            generic_args[0]
        )

        expected_argument_type: tuple[type, ...] | type = _unpack_generic_args(
            generic_args[1]
        )

        if not isinstance(expected_value_type, tuple):
            expected_value_types = (expected_value_type, )
        else:
            expected_value_types = expected_value_type

        if not isinstance(expected_argument_type, tuple):
            expected_argument_type = (expected_argument_type, )
        else:
            expected_argument_type = expected_argument_type

        if self._preferred_value_type:
            if self._preferred_value_type not in expected_value_types and Any not in expected_value_types:
                raise HandlerInvalidPreferredValueType(
                    self, expected_value_type=expected_value_types
                )

            return HandlerExpectedTypes(
                value=(self._preferred_value_type, ),
                argument=expected_argument_type
            )

        return HandlerExpectedTypes(
            value=expected_value_types, argument=expected_argument_type
        )

    @property
    def _expected_value_type(self) -> tuple[type, ...]:
        return self._expected_types.value

    @property
    def _expected_argument_type(self) -> tuple[type, ...]:
        return self._expected_types.argument
