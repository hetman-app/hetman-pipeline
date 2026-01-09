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
            HandlerMode.ROOT: lambda _: "Must contain only lowercase letters (a-z)."
        }

        def query(self):
            return self.fullmatch(r"^[a-z]+$")

    class LowercaseWithSpaces(MatchHandler[str, None]):
        """Accepts lowercase English letters (a-z) and spaces"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _:
                "Must contain only lowercase letters and spaces (e.g., 'hello world')."
        }

        def query(self):
            return self.fullmatch(r"^[a-z ]+$")

    class Uppercase(MatchHandler[str, None]):
        """Accepts ONLY uppercase English letters (A-Z)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Must contain only uppercase letters (A-Z)."
        }

        def query(self):
            return self.fullmatch(r"^[A-Z]+$")

    class UppercaseWithSpaces(MatchHandler[str, None]):
        """Accepts uppercase English letters (A-Z) and spaces"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _:
                "Must contain only uppercase letters and spaces (e.g., 'HELLO WORLD')."
        }

        def query(self):
            return self.fullmatch(r"^[A-Z ]+$")

    class Letters(MatchHandler[str, None]):
        """Accepts ONLY case English letters (a-z, A-Z)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Must contain only letters (a-z, A-Z)."
        }

        def query(self):
            return self.fullmatch(r"^[a-zA-Z]+$")

    class LettersWithSpaces(MatchHandler[str, None]):
        """Accepts English letters (a-z, A-Z) and spaces"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _:
                "Must contain only letters and spaces (e.g., 'Hello World')."
        }

        def query(self):
            return self.fullmatch(r"^[a-zA-Z ]+$")

    class Digits(MatchHandler[str, None]):
        """Accepts ONLY numeric digits (0-9)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Must contain only digits (0-9)."
        }

        def query(self):
            return self.fullmatch(r"^\d+$")

    class DigitsWithSpaces(MatchHandler[str, None]):
        """Accepts numeric digits (0-9) and spaces"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _:
                "Must contain only digits and spaces (e.g., '123 456')."
        }

        def query(self):
            return self.fullmatch(r"^[\d ]+$")

    class Alphanumeric(MatchHandler[str, None]):
        """Accepts letters and numeric digits. No symbols or spaces"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Must contain only letters and digits (e.g., 'abc123')."
        }

        def query(self):
            return self.fullmatch(r"^[a-zA-Z0-9]+$")

    class AlphanumericWithSpaces(MatchHandler[str, None]):
        """Accepts letters, numeric digits, and spaces. No symbols"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _:
                "Must contain only letters, digits, and spaces (e.g., 'abc 123')."
        }

        def query(self):
            return self.fullmatch(r"^[a-zA-Z0-9 ]+$")

    class Printable(MatchHandler[str, None]):
        """Accepts letters, numbers, symbols, and spaces (ASCII 20-7E)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _:
                "Contains invalid characters. Only printable ASCII characters are allowed."
        }

        def query(self):
            return self.fullmatch(r"^[ -~]+$")

    class NoWhitespace(MatchHandler[str, None]):
        """Ensures string contains no spaces, tabs, or line breaks"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Must not contain spaces, tabs, or line breaks."
        }

        def query(self):
            return not self.search(r"\s")

    class Slug(MatchHandler[str, None]):
        """URL-friendly strings: 'my-cool-post-123'"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _:
                "Must contain only lowercase letters, numbers, and hyphens (e.g., 'my-post-123')."
        }

        def query(self):
            return self.fullmatch(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
