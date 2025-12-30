from __future__ import annotations

import re

from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.base_handler.resources.exceptions import \
    HandlerException
from pipeline.handlers.match_handler.match_handler import MatchHandler


class MatchFormat:
    """
    Registry for format-related match handlers.

    Includes handlers for Email, UUID, HexColor, etc.
    """
    class Email(MatchHandler[str, None]):
        """Accepts email addresses with standard user, domain, and TLD parts"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Invalid email address format."
        }

        def query(self):
            return self.fullmatch(
                r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            )

    class UUID(MatchHandler[str, None]):
        """Validates 36-character hexadecimal unique identifiers (8-4-4-4-12)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {HandlerMode.ROOT: lambda _: "Invalid UUID format."}

        def query(self):
            return self.fullmatch(
                r"^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$", re.IGNORECASE
            )

    class HexColor(MatchHandler[str, None]):
        """Accepts hex colors in 3 or 6 digit formats (e.g., #F00, #FF0000)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Must be a valid hex color code (e.g., #FFFFFF)."
        }

        def query(self):
            return self.fullmatch(r"^#(?:[0-9a-fA-F]{3}){1,2}$")

    class E164Phone(MatchHandler[str, None]):
        """International phone numbers in E.164 format (e.g., +1234567890)"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Invalid international phone format (E.164)."
        }

        def query(self):
            return self.fullmatch(r"^\+[1-9]\d{1,14}$")

    class Password(MatchHandler[str, str]):
        """Validates password strength based on three policies: RELAXED, NORMAL, or STRICT.
        
        Policies:
        - RELAXED: 6-64 chars, 1 uppercase, 1 lowercase.
        - NORMAL: 6-64 chars, 1 uppercase, 1 lowercase, 1 digit.
        - STRICT: 6-64 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special character.
        
        Requires a policy argument (e.g., Match.Format.Password.NORMAL)
        """
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        RELAXED = "relaxed"
        NORMAL = "normal"
        STRICT = "strict"

        ERROR_MESSAGE = {
            RELAXED: "Min 6, Max 64, 1 Upper, 1 Lower",
            NORMAL: "Min 6, Max 64, 1 Upper, 1 Lower, 1 Digit",
            STRICT: "Min 6, Max 64, 1 Upper, 1 Lower, 1 Digit, 1 Special"
        }

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda self: self.ERROR_MESSAGE[self.argument]  # type: ignore
        }

        def query(self):
            if self.argument == self.RELAXED:
                # Min 6, Max 64, 1 Upper, 1 Lower
                pattern = r"^(?=.*[a-z])(?=.*[A-Z]).{6,64}$"
            elif self.argument == self.NORMAL:
                # Min 6, Max 64, 1 Upper, 1 Lower, 1 Digit
                pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,64}$"
            elif self.argument == self.STRICT:
                # Min 6, Max 64, 1 Upper, 1 Lower, 1 Digit, 1 Special
                pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{6,64}$"
            else:
                raise HandlerException(
                    f"{self.argument} is not a valid password policy. Use Password.RELAXED, Password.NORMAL, or Password.STRICT."
                )

            return self.fullmatch(pattern)
