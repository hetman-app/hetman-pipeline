from __future__ import annotations

from typing import TYPE_CHECKING

from pipeline.handlers.base_handler.resources.constants import HandlerMode

if TYPE_CHECKING:
    from pipeline.handlers.base_handler.base_handler import BaseHandler


class HandlerException(Exception):
    pass


class HandlerInvalidValueType(HandlerException):
    def __init__(self, handler: BaseHandler) -> None:
        expected_types = handler._expected_value_type
        received_type = type(handler.value)

        expected_str = ", ".join([t.__name__ for t in expected_types])

        error: str = (
            f"Value type mismatch in handler '{handler.id}'. "
            f"Expected type(s): {expected_str}. "
            f"Received type: {received_type.__name__}. "
            f"Value: {repr(handler.value)}."
        )

        super().__init__(error)


class HandlerInvalidPreferredValueType(HandlerException):
    def __init__(
        self, handler: BaseHandler, expected_value_type: tuple[type, ...]
    ) -> None:
        received_type = handler._preferred_value_type

        if received_type:
            received_type_str = received_type.__name__
        else:
            received_type_str = "None"

        expected_str = ", ".join([t.__name__ for t in expected_value_type])

        error: str = (
            f"Preferred value type mismatch in handler '{handler.id}'. "
            f"Expected type(s): {expected_str}. "
            f"Received type: {received_type_str}. "
        )

        super().__init__(error)


class HandlerInvalidArgumentType(HandlerException):
    def __init__(self, handler: BaseHandler) -> None:
        expected_types = handler._expected_argument_type
        received_type = type(handler.argument)

        expected_str = ", ".join([t.__name__ for t in expected_types])

        error: str = (
            f"Argument type mismatch in handler '{handler.__class__}'. "
            f"Expected type(s): {expected_str}. "
            f"Received type: {received_type.__name__}. "
            f"Value: {repr(handler.value)}. "
            f"Argument: {repr(handler.argument)}."
        )

        super().__init__(error)


class HandlerModeException(HandlerException):
    pass


class HandlerModeUnsupported(HandlerModeException):
    def __init__(self, handler_mode: HandlerMode) -> None:
        error: str = f"This condition does not support \"{handler_mode.value}\" mode."

        super().__init__(error)


class HandlerModeMissingContextValue(HandlerModeException):
    def __init__(self, argument: str) -> None:
        error: str = f"Condition mode is context, but there is missing context value for specifed context key \"{argument}\"."

        super().__init__(error)
