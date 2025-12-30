from __future__ import annotations

import json

from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.match_handler.match_handler import MatchHandler


class MatchEncoding:
    """
    Registry for encoding-related match handlers.

    Includes handlers for Base64, JSON, etc.
    """
    class Base64(MatchHandler[str, None]):
        """Checks if string is valid Base64 encoded"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Invalid Base64 encoding."
        }

        def query(self):
            return self.fullmatch(
                r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$"
            )

    class JSON(MatchHandler[str, None]):
        """Validates that a string is a correctly formatted JSON object or array"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "String is not valid JSON."
        }

        def query(self):
            try:
                json.loads(self.value)

                return True
            except (ValueError, TypeError):
                return False
