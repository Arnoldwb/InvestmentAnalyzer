from pathlib import Path


# Investment Analyzer's persistent working folder.
#
# This location is independent of where the Python source code
# or packaged Mac application is installed.
PROJECT_ROOT = Path.home() / "InvestmentAnalyzer"

# Standard application folders.
DATA_DIR = PROJECT_ROOT / "data"
PORTFOLIO_DIR = PROJECT_ROOT / "portfolios"
REPORTS_DIR = PROJECT_ROOT / "reports"
OUTPUT_DIR = PROJECT_ROOT / "output"
DOCS_DIR = PROJECT_ROOT / "docs"


def ensure_application_directories() -> None:
    """
    Ensure that the standard Investment Analyzer directories exist.
    """

    for directory in (
        DATA_DIR,
        PORTFOLIO_DIR,
        REPORTS_DIR,
        OUTPUT_DIR,
        DOCS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


ensure_application_directories()
