from __future__ import annotations

from functools import partial
from typing import Optional, Type, TypeVar

from pipeline.handlers.base_handler.base_handler import BaseHandler
from pipeline.handlers.base_handler.resources.constants import HandlerMode

T = TypeVar('T', bound=BaseHandler)


def Context(handler: Type[T]):
    """
    Modifier ensure the handler is run in CONTEXT mode.

    In CONTEXT mode, the handler's argument is retrieved from the pipeline context
    using the provided argument as a key.

    Args:
        handler (Type[T]): The handler class to modify.

    Returns:
        partial: A partial application of the handler with _mode=HandlerMode.CONTEXT.
    """
    return partial(handler, _mode=HandlerMode.CONTEXT)


def Item(
    handler: Type[T] | partial[T],
    use_key: Optional[bool] = False,
    only_consider: Optional[type] = None
):
    """
    Modifier to ensure the handler is run in ITEM mode.

    In ITEM mode, the handler is applied to each item in an iterable.

    Args:
        handler (Type[T] | partial[T]): The handler class or partial to modify.
        use_key (Optional[bool]): If True, the handler uses the item's key (e.g., in a dictionary) instead of value.
        only_consider (Optional[type]): Specific type to filter items for processing.

    Returns:
        partial: A partial application of the handler with ITEM mode settings.
    """
    return partial(
        handler,
        _mode=HandlerMode.ITEM,
        _item_use_key=use_key,
        _preferred_value_type=only_consider
    )
