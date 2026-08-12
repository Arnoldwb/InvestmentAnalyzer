from pathlib import Path
import sys


def get_project_root() -> Path:
    """
    Return the persistent Investment Analyzer working folder.

    Development runs continue to use the existing project folder.
    Packaged Mac applications use the dedicated user-data folder.

    This keeps application data independent of the installed
    application bundle.
    """

    if getattr(sys, "frozen", False):
        return Path.home() / "!InvestmentAnalyzer"

    return Path.home() / "InvestmentAnalyzer"


# Investment Analyzer's persistent working folder.
PROJECT_ROOT = get_project_root()

# Standard application folders.
DATA_DIR = PROJECT_ROOT / "data"
DATA_BACKUP_DIR = PROJECT_ROOT / "data_backups"
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
        DATA_BACKUP_DIR,
        PORTFOLIO_DIR,
        REPORTS_DIR,
        OUTPUT_DIR,
        DOCS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


ensure_application_directories()
