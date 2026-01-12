from __future__ import annotations

from typing import Any, Iterable

from pipeline.core.pipeline.pipeline import Pipeline
from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.condition_handler.resources.constants import \
    ConditionFlag

from .condition_handler import ConditionHandler


class Condition:
    """
    Registry for all condition handlers.

    This class groups all available condition handlers (e.g., ValueType, MinLength, Equal)
    for easy access.
    """
    class ValueType(ConditionHandler[Any, type]):
        """
        A built-in condition handler to validate the type of the value.
        
        This handler is automatically used by the Pipe to ensure the passed value matches
        the expected type defined in the Pipe.
        """
        FLAGS = (ConditionFlag.BREAK_PIPE_LOOP_ON_ERROR, )

        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda self: f"Invalid type. Expected {self.argument.__name__}."
        }

        def query(self):
            return isinstance(self.value, self.argument)

    class MinLength(ConditionHandler[str | list | dict, int]):
        """Ensures the collection or string has at least N items/characters"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda self:
                f"Too short. Minimum length is {self.argument} characters."
                if isinstance(self.value, str) else
                f"Too few items. Minimum count is {self.argument}."
        }

        def query(self):
            return len(self.value) >= self.argument

    class MaxLength(ConditionHandler[str | list | dict, int]):
        """Ensures the collection or string does not exceed N items/characters"""
        FLAGS = (ConditionFlag.BREAK_PIPE_LOOP_ON_ERROR, )

        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda self:
                f"Too long. Maximum length is {self.argument} characters."
                if isinstance(self.value, str) else
                f"Too many items. Maximum count is {self.argument}."
        }

        def query(self):
            return len(self.value) <= self.argument

    class ExactLength(ConditionHandler[str | list | dict, int]):
        """Ensures the collection or string is exactly N items/characters long"""
        FLAGS = (ConditionFlag.BREAK_PIPE_LOOP_ON_ERROR, )

        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda self:
                f"Invalid length. Must be exactly {self.argument} characters."
                if isinstance(self.value, str) else
                f"Invalid count. Must contain exactly {self.argument} items."
        }

        def query(self):
            return len(self.value) == self.argument

    class MinNumber(ConditionHandler[int | float, int | float]):
        """Ensures the numeric value is greater than or equal to N"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM, HandlerMode.CONTEXT)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda self: f"Value must be at least {self.argument}."
        }

        def query(self):
            return self.value >= self.argument

    class MaxNumber(ConditionHandler[int | float, int | float]):
        """Ensures the numeric value is less than or equal to N"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM, HandlerMode.CONTEXT)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda self: f"Value must be at most {self.argument}."
        }

        def query(self):
            return self.value <= self.argument

    class IncludedIn(ConditionHandler[Any, Iterable]):
        """Ensures the value exists within the provided Iterable"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda self:
                f"Selected option is invalid. Please choose from the {list(self.argument)}."
        }

        def query(self):
            return self.value in self.argument

    class NotIncludedIn(ConditionHandler[Any, Iterable]):
        """Ensures the value does not exist within the provided blacklist"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "This value is not allowed."
        }

        def query(self):
            return self.value not in self.argument

    class Equal(ConditionHandler[Any, Any]):
        """Ensures the value is strictly equal to the argument or a specific context field"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM, HandlerMode.CONTEXT)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Value does not match the expected value."
        }

        def query(self):
            return self.value == self.argument

    class NotEqual(ConditionHandler[Any, Any]):
        """Ensures the value is strictly not equal to the argument or a specific context field"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM, HandlerMode.CONTEXT)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Value must be different."
        }

        def query(self):
            return self.value != self.argument

    class MatchesField(ConditionHandler[Any, Any]):
        """Validates that the current value matches the value of another field in the context (e.g., password confirmation)"""
        SUPPORT = (HandlerMode.CONTEXT, )

        ERROR_TEMPLATES = {
            HandlerMode.CONTEXT:
                lambda self: f'Must match the "{self.input_argument}" field.'
        }

        def query(self):
            return self.value == self.argument

    class DoesNotMatchField(ConditionHandler[Any, Any]):
        """Validates that the current value does not match the value of another field in the context (e.g., new password != old password)"""
        SUPPORT = (HandlerMode.CONTEXT, )

        ERROR_TEMPLATES = {
            HandlerMode.CONTEXT:
                lambda self:
                f'Must be different from the "{self.input_argument}" field.'
        }

        def query(self):
            return self.value != self.argument

    class Pipeline(ConditionHandler[dict, Pipeline]):
        """Validates a dictionary using the same rules as the normal pipeline, but for nested data."""
        SUPPORT = (HandlerMode.ROOT, )

        ERROR_BUILDER = lambda self: self.metadata['errors']

        ERROR_TEMPLATES = {HandlerMode.ROOT: lambda _: None}

        def query(self):
            self.metadata['errors'] = self.argument.run(data=self.value).errors

            return self.metadata['errors'] is None
