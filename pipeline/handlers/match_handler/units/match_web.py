from __future__ import annotations

from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.match_handler.match_handler import MatchHandler


class MatchWeb:
    """
    Registry for web-related match handlers.

    Includes handlers for Domain and URL.
    """

    class Domain(MatchHandler[str, None]):
        """Validates a domain name based on RFC 1035."""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {HandlerMode.ROOT: lambda _: "Invalid domain format."}

        def query(self):
            return self.fullmatch(
                r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
            )

    class URL(MatchHandler[str, None]):
        """Validates web URLs using HTTP or HTTPS protocols."""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {HandlerMode.ROOT: lambda _: "Invalid URL format."}

        def query(self):
            return self.fullmatch(
                r"^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
            )
