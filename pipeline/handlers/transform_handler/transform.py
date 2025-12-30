import re
from typing import Optional

from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.transform_handler.transform_handler import \
    TransformHandler


class Transform:
    """
    Central registry for all transform handlers.

    Transform handlers modify the value in some way, such as changing case,
    replacing substrings, or performing arithmetic operations.
    """
    class Strip(TransformHandler[str, Optional[str]]):
        """Removes leading and trailing whitespace from a string"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            return self.value.strip()

    class Capitalize(TransformHandler[str, None]):
        """Converts the first character to uppercase and the rest to lowercase"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            return self.value.capitalize()

    class Lowercase(TransformHandler[str, None]):
        """Converts all characters in the string to lowercase"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            return self.value.lower()

    class Uppercase(TransformHandler[str, None]):
        """Converts all characters in the string to uppercase"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            return self.value.upper()

    class Multiply(TransformHandler[str | list | int | float, int | float]):
        """
        Multiplies a string, list, integer or float by the provided argument
        
        If the value is not numeric, the argument is rounded before multiplication.
        """
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            if not isinstance(self.value, (int, float)):
                return self.value * round(self.argument)

            return self.value * self.argument

    class Reverse(TransformHandler[str | list, None]):
        """Reverses the order of characters in a string or items in a list"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            return self.value[::-1]

    class Title(TransformHandler[str, None]):
        """Converts the first character of every word to uppercase"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            return self.value.title()

    class SnakeCase(TransformHandler[str, None]):
        """Converts strings to snake_case (e.g., 'HelloWorld' -> 'hello_world')"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            s = re.sub(r'(?<!^)(?=[A-Z])', '_', self.value).lower()

            return s.replace("-", "_").replace(" ", "_")

    class Unique(TransformHandler[list, None]):
        """Removes duplicate items from a list while preserving order"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            return list(dict.fromkeys(self.value))

    class Replace(TransformHandler[str, tuple]):
        """Replaces all occurrences of a substring with another (old, new)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        def operation(self):
            old, new = self.argument

            return self.value.replace(old, new)
