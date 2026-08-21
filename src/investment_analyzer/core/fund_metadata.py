import json

from investment_analyzer.core.paths import DATA_DIR

METADATA_FILE = DATA_DIR / "fund_metadata.json"


def load_fund_metadata() -> dict:
    """
    Load fund metadata from the local metadata file.
    """

    if not METADATA_FILE.exists():
        return {}

    try:
        with METADATA_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(data, dict):
        return {}

    return data


def get_fund_name(symbol: str) -> str:
    """
    Return the stored fund name for a symbol.

    Return the symbol itself if no name is available.
    """

    symbol = symbol.strip().upper()

    if not symbol:
        return ""

    metadata = load_fund_metadata()

    entry = metadata.get(symbol)

    if not isinstance(entry, dict):
        return symbol

    name = entry.get("name")

    if not isinstance(name, str):
        return symbol

    name = name.strip()

    return name or symbol
