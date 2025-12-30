from __future__ import annotations

from abc import abstractmethod
from typing import cast

from pipeline.handlers.base_handler.base_handler import A, BaseHandler, V
from pipeline.handlers.base_handler.resources.exceptions import \
    HandlerModeException


class TransformHandler(BaseHandler[V, A]):
    """
    Abstract base class for transform handlers.

    Transform handlers modify the input value and return the transformed value.
    They must implement the `operation` method.
    """
    @abstractmethod
    def operation(self) -> V:
        """
        Performs the transformation operation.

        Returns:
            V: The transformed value.
        """
        ...

    def _handle(self) -> V:
        """
        Handles the transformation in ROOT or CONTEXT mode.

        Returns:
            V: The transformed value.
        """
        return self.operation()

    def _handle_item_mode(self) -> V:
        """
        Handles the transformation in ITEM mode (for iterables).

        Iterates over the input value and applies the transformation to each item.
        The input value is modified in place if it's a list or dict.

        Returns:
            V: The transformed iterable (same object as input, but modified).
        
        Raises:
            HandlerModeException: If the input value is not a list or dict.
        """
        if isinstance(self.input_value, list):
            items = enumerate(self.input_value)
        elif isinstance(self.input_value, dict):
            items = self.input_value.items()
        else:
            raise HandlerModeException(
                "The transform handler input value is not of type list or dict."
            )

        for key, value in items:
            if self._item_use_key:
                value = key

            if not self._is_valid_type(value, self._expected_value_type):
                continue

            # NOTE: We use can cast() here because we checked if the value type is valid but linter does not know that.
            self.value = cast(V, value)

            self.input_value[key] = self.operation()

        return self.input_value
