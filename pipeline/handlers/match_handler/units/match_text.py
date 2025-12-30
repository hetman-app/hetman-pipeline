from __future__ import annotations

from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.match_handler.match_handler import MatchHandler


class MatchText:
    """
    Registry for text-related match handlers.

    Includes handlers for Lowercase, Uppercase, Digits, etc.
    """
    class Lowercase(MatchHandler[str, None]):
        """Accepts ONLY lowercase English letters (a-z)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Can only contain lowercase letters."
        }

        def query(self):
            return self.fullmatch(r"^[a-z]+$")

    class Uppercase(MatchHandler[str, None]):
        """Accepts ONLY uppercase English letters (A-Z)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Can only contain uppercase letters."
        }

        def query(self):
            return self.fullmatch(r"^[A-Z]+$")

    class Letters(MatchHandler[str, None]):
        """Accepts ONLY case English letters (a-z, A-Z)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Can only contain letters."
        }

        def query(self):
            return self.fullmatch(r"^[a-zA-Z]+$")

    class Digits(MatchHandler[str, None]):
        """Accepts ONLY numeric digits (0-9)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Can only contain digits."
        }

        def query(self):
            return self.fullmatch(r"^\d+$")

    class Alphanumeric(MatchHandler[str, None]):
        """Accepts letters and numeric digits. No symbols or spaces"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Can only contain letters and digits."
        }

        def query(self):
            return self.fullmatch(r"^[a-zA-Z0-9]+$")

    class Printable(MatchHandler[str, None]):
        """Accepts letters, numbers, symbols, and spaces (ASCII 20-7E)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Contains invalid or non-printable characters."
        }

        def query(self):
            return self.fullmatch(r"^[ -~]+$")

    class NoWhitespace(MatchHandler[str, None]):
        """Ensures string contains no spaces, tabs, or line breaks"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Cannot contain spaces or tabs."
        }

        def query(self):
            return not self.search(r"\s")

    class Slug(MatchHandler[str, None]):
        """URL-friendly strings: 'my-cool-post-123'"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Must be lowercase letters, numbers, and hyphens."
        }

        def query(self):
            return self.fullmatch(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
