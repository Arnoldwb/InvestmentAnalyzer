"""
Mapping between imported historical security names and fund symbols.
"""

HISTORICAL_SECURITY_SYMBOLS = {
    "Vanguard Wellington Admiral": "VWENX",
    "Vanguard Health Care-Admiral": "VGHAX",
    "Vanguard Federal Money Market Fund": "VMFXX",
}


def historical_security_to_symbol(security_name: str) -> str | None:
    """
    Return the Investment Analyzer symbol for a historical security name.

    Return None when no known mapping exists. Unknown securities are
    intentionally not guessed.
    """

    name = security_name.strip()

    if not name:
        return None

    return HISTORICAL_SECURITY_SYMBOLS.get(name)
