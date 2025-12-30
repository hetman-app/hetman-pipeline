from __future__ import annotations

from zoneinfo import available_timezones

from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.match_handler.match_handler import MatchHandler
from pipeline.handlers.match_handler.units.resources.constants import (
    ISO_639_1, ISO_3166, ISO_4217
)


class MatchLocalization:
    """
    Registry for localization-related match handlers.

    Includes handlers for Country, Currency, Language (ISO codes), and Timezones.
    """
    class Country(MatchHandler[str, None]):
        """ISO 3166-1 alpha-2 (e.g., 'US', 'DE', 'JP')"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Must be a valid 2-letter ISO country code."
        }

        def query(self):
            return self.value in ISO_3166

    class Currency(MatchHandler[str, None]):
        """ISO 4217 (e.g., 'USD', 'EUR', 'BTC')"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Must be a valid 3-letter currency code."
        }

        def query(self):
            return self.value in ISO_4217

    class Language(MatchHandler[str, None]):
        """ISO 639-1 (e.g., 'en', 'fr', 'zh')"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT:
                lambda _: "Must be a valid 2-letter language code."
        }

        def query(self):
            return self.value in ISO_639_1

    class Timezone(MatchHandler[str, None]):
        """IANA Timezone (e.g., 'America/New_York', 'Europe/London')"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Invalid IANA timezone string."
        }

        def query(self):
            return self.value in available_timezones()
