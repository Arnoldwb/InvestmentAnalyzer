import json
from pathlib import Path

from investment_analyzer.core.paths import PROJECT_ROOT
from investment_analyzer.models.portfolio import Portfolio


PORTFOLIO_DIR = PROJECT_ROOT / "portfolios"


def ensure_portfolio_directory() -> Path:
    """
    Ensure that the portfolio storage directory exists.
    """
    PORTFOLIO_DIR.mkdir(exist_ok=True)

    return PORTFOLIO_DIR


def save_portfolio(portfolio: Portfolio, filename: str | None = None) -> Path:
    """
    Save a Portfolio to a JSON file.

    If no filename is supplied, the portfolio name is used.
    """
    portfolio.validate()

    directory = ensure_portfolio_directory()

    if filename is None:
        safe_name = portfolio.name.strip().replace(" ", "_")

        if not safe_name:
            safe_name = "Portfolio"

        filename = f"{safe_name}.json"

    if not filename.lower().endswith(".json"):
        filename += ".json"

    path = directory / filename

    data = {
        "name": portfolio.name,
        "holdings": [
            {
                "symbol": holding.fund.symbol,
                "allocation": holding.allocation,
            }
            for holding in portfolio.holdings
        ],
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return path


def load_portfolio(filename: str) -> Portfolio:
    """
    Load a Portfolio from a JSON file.
    """
    directory = ensure_portfolio_directory()

    if not filename.lower().endswith(".json"):
        filename += ".json"

    path = directory / filename

    if not path.exists():
        raise FileNotFoundError(f"Portfolio file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    portfolio = Portfolio(data.get("name", "Portfolio"))

    for holding in data.get("holdings", []):
        portfolio.add_fund(
            holding["symbol"],
            float(holding["allocation"]),
        )

    portfolio.validate()

    return portfolio


def list_portfolios() -> list[str]:
    """
    Return the names of all saved portfolio files.
    """
    directory = ensure_portfolio_directory()

    return sorted(
        path.name
        for path in directory.glob("*.json")
    )
