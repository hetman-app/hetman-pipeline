from __future__ import annotations

from typing import ClassVar, Type

from pipeline.handlers.match_handler.units.match_encoding import MatchEncoding
from pipeline.handlers.match_handler.units.match_format import MatchFormat
from pipeline.handlers.match_handler.units.match_localization import \
    MatchLocalization
from pipeline.handlers.match_handler.units.match_network import MatchNetwork
from pipeline.handlers.match_handler.units.match_regex import MatchRegex
from pipeline.handlers.match_handler.units.match_text import MatchText
from pipeline.handlers.match_handler.units.match_time import MatchTime
from pipeline.handlers.match_handler.units.match_web import MatchWeb


class Match:
    """
    Central registry for all match handler units.

    This class provides a convenient way to access different match handlers
    (e.g., Text, Regex, Web) from a single location.
    """
    Text: ClassVar[Type[MatchText]] = MatchText
    Regex: ClassVar[Type[MatchRegex]] = MatchRegex

    Web: ClassVar[Type[MatchWeb]] = MatchWeb
    Network: ClassVar[Type[MatchNetwork]] = MatchNetwork

    Time: ClassVar[Type[MatchTime]] = MatchTime
    Localization: ClassVar[Type[MatchLocalization]] = MatchLocalization

    Format: ClassVar[Type[MatchFormat]] = MatchFormat
    Encoding: ClassVar[Type[MatchEncoding]] = MatchEncoding
