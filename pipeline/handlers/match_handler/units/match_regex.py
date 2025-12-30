from __future__ import annotations

from re import Pattern

from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.match_handler.match_handler import MatchHandler


class MatchRegex:
    """
    Registry for regex-related match handlers.

    Includes handlers for Search and FullMatch.
    """
    class Search(MatchHandler[str, str | Pattern]):
        """Accepts values that contain at least one match of the provided regex pattern"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda self:
                f"Invalid value. Valid pattern for value is {self.argument}."
        }

        def query(self):
            return self.search(self.argument)

    class FullMatch(MatchHandler[str, str | Pattern]):
        """Accepts values that match the provided regex pattern in their entirety"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda self:
                f"Invalid value. Valid pattern for value is {self.argument}."
        }

        def query(self):
            return self.fullmatch(self.argument)
