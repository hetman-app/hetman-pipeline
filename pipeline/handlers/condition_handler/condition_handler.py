from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Optional, cast

from pipeline.handlers.base_handler.base_handler import A, BaseHandler, V
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.base_handler.resources.exceptions import \
    HandlerModeException
from pipeline.handlers.condition_handler.resources.constants import \
    ConditionFlag
from pipeline.handlers.condition_handler.resources.exceptions import \
    ConditionMissingRootErrorMsg

if TYPE_CHECKING:
    from pipeline.core.pipe.resources.types import PipeContext, PipeMetadata
    from pipeline.handlers.condition_handler.resources.types import (
        ConditionError, ConditionErrorTemplates
    )


def default_error_builder(self: "ConditionHandler"):
    if ConditionFlag.RETURN_ONLY_ERROR_MSG in self.FLAGS:
        return self.error_msg

    return {'id': self.id, 'msg': self.error_msg, 'value': self.value}


class ConditionHandler(BaseHandler[V, A]):
    """
    Abstract base class for specific condition implementations.

    This class provides the infrastructure for condition checking, including error message generation
    and support for different handling modes (ROOT, ITEM).
    It expects subclasses to implement the `query` method.
    """
    ERROR_BUILDER: ClassVar[Callable[['ConditionHandler'],
                                     ConditionError]] = default_error_builder

    ERROR_TEMPLATES: ClassVar[ConditionErrorTemplates]

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
        Initializes the ConditionHandler.
        
        It ensures that if ROOT mode is supported, a corresponding error template is present.
        """
        super().__init__(
            value, argument, context, metadata, _mode, _item_use_key,
            _preferred_value_type
        )

        if HandlerMode.ROOT in self.SUPPORT and HandlerMode.ROOT not in self.ERROR_TEMPLATES:
            raise ConditionMissingRootErrorMsg()

    @abstractmethod
    def query(self) -> bool:
        """
        Performs the condition check.

        Returns:
            bool: True if the condition is met, False otherwise.
        """
        ...

    def _handle(self) -> Optional[ConditionError]:
        """
        Handles the condition check in ROOT or CONTEXT mode.

        Returns:
            Optional[ConditionError]: An error object if the check fails, None otherwise.
        """
        if not self.query():
            return self.ERROR_BUILDER()

    def _handle_item_mode(self) -> Optional[dict[str | int, ConditionError]]:
        """
        Handles the condition check in ITEM mode (for iterables).

        Iterates over the input value and applies the check to each item.

        Returns:
            Optional[dict[str | int, ConditionError]]: A dictionary of errors keyed by item index/key,
            or None if no errors occurred.
        
        Raises:
            HandlerModeException: If the input value is not a supported iterable type.
        """
        errors = {}

        if isinstance(self.input_value, (list, tuple, set)):
            items = enumerate(self.input_value)
        elif isinstance(self.input_value, dict):
            items = self.input_value.items()
        else:
            raise HandlerModeException(
                "The condition/match handler input value is not of type list, tuple, set, or dict."
            )

        for key, value in items:
            if self._item_use_key:
                value = key

            if not self._is_valid_type(value, self._expected_value_type):
                continue

            # NOTE: We use can cast() here because we checked if the value type is valid but linter does not know that.
            self.value = cast(V, value)

            self._item_index = key

            if not self.query():
                errors[key] = (self.ERROR_BUILDER())

        return errors if errors else None

    @property
    def error_msg(self) -> Any:
        """
        Generates the error message based on the current mode and error templates.

        Returns:
            Any: The generated error message.
        
        Raises:
            ConditionMissingRootErrorMsg: If the root error template is missing.
        """
        if self._mode in self.ERROR_TEMPLATES:
            return self.ERROR_TEMPLATES[self._mode](self)

        if HandlerMode.ROOT not in self.ERROR_TEMPLATES:
            raise ConditionMissingRootErrorMsg()

        return self.ERROR_TEMPLATES[HandlerMode.ROOT](self)
