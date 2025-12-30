import re
from typing import Optional

from pipeline.handlers.base_handler.base_handler import A, V
from pipeline.handlers.condition_handler.condition_handler import \
    ConditionHandler


class MatchHandler(ConditionHandler[V, A]):
    """
    Base class for match handlers.

    Match handlers extend condition handlers to provide specific matching capabilities,
    often involving regular expressions or patterns.
    """
    def search(
        self,
        pattern: str | re.Pattern,
        flag: Optional[re.RegexFlag] = None
    ) -> bool:
        """
        Searches for the pattern in the value.

        Args:
            pattern (str | re.Pattern): The regex pattern to search for.
            flag (Optional[re.RegexFlag]): Optional regex flags.

        Returns:
            bool: True if the pattern is found, False otherwise.
        """
        return re.search(pattern, str(self.value), flag or 0) is not None

    def fullmatch(
        self,
        pattern: str | re.Pattern,
        flag: Optional[re.RegexFlag] = None
    ) -> bool:
        """
        Checks if the entire value matches the pattern.

        Args:
            pattern (str | re.Pattern): The regex pattern to match against.
            flag (Optional[re.RegexFlag]): Optional regex flags.

        Returns:
            bool: True if the entire value matches the pattern, False otherwise.
        """
        return re.fullmatch(pattern, str(self.value), flag or 0) is not None
