from __future__ import annotations

from ipaddress import ip_address

from pipeline.handlers.base_handler.resources.constants import HandlerMode
from pipeline.handlers.match_handler.match_handler import MatchHandler


class MatchNetwork:
    """
    Registry for network-related match handlers.

    Includes handlers for IPv4, IPv6, MAC Addresses, etc.
    """
    class IPv4(MatchHandler[str, None]):
        """Validates a standard IPv4 address (e.g., '192.168.1.1')"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {HandlerMode.ROOT: lambda _: "Invalid IPv4 address."}

        def query(self):
            try:
                return ip_address(address=self.value).version == 4
            except:
                return False

    class IPv6(MatchHandler[str, None]):
        """Validates an IPv6 address (e.g., '2001:db8::ff00:42:8329')"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {HandlerMode.ROOT: lambda _: "Invalid IPv6 address."}

        def query(self):
            try:
                return ip_address(address=self.value).version == 6
            except:
                return False

    class MACAddress(MatchHandler[str, None]):
        """Accepts hardware MAC addresses using colon, hyphen, or dot separators"""
        SUPPORT = (HandlerMode.ROOT, HandlerMode.ITEM)

        ERROR_TEMPLATES = {
            HandlerMode.ROOT: lambda _: "Invalid MAC address format."
        }

        def query(self):
            return self.fullmatch(
                r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})|([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})$"
            )
