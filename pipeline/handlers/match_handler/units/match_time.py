from __future__ import annotations

from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.match_handler.match_handler import MatchHandler


class MatchTime:
    """
    Registry for time-related match handlers.

    Includes handlers for Date, Time, and DateTime (ISO 8601).
    """
    class Date(MatchHandler[str, None]):
        """Validates YYYY-MM-DD format"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Date must be in YYYY-MM-DD format."
        }

        def query(self):
            return self.fullmatch(
                r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
            )

    class Time(MatchHandler[str, None]):
        """Validates 24h time in HH:MM or HH:MM:SS format"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Invalid time format (HH:MM[:SS])."
        }

        def query(self):
            return self.fullmatch(r"^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$")

    class DateTime(MatchHandler[str, None]):
        """Validates ISO 8601 combined Date and Time (e.g., 2023-10-01T14:30:00Z)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Invalid ISO 8601 DateTime format."
        }

        def query(self):
            return self.fullmatch(
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$"
            )
