from pathlib import Path
import sys

from investment_analyzer.core.paths import get_project_root


def test_development_project_root():
    """
    Development mode must continue using ~/InvestmentAnalyzer.
    """

    original_frozen = getattr(sys, "frozen", None)

    try:
        if hasattr(sys, "frozen"):
            del sys.frozen

        root = get_project_root()

        assert root == (
            Path.home() / "InvestmentAnalyzer"
        )

    finally:
        if original_frozen is None:
            if hasattr(sys, "frozen"):
                del sys.frozen
        else:
            sys.frozen = original_frozen


def test_packaged_project_root():
    """
    Packaged Mac applications must use ~/!INVESTMENT_ANALYZER.
    """

    original_frozen = getattr(sys, "frozen", None)

    try:
        sys.frozen = True

        root = get_project_root()

        assert root == (
            Path.home() / "!INVESTMENT_ANALYZER"
        )

    finally:
        if original_frozen is None:
            if hasattr(sys, "frozen"):
                del sys.frozen
        else:
            sys.frozen = original_frozen


if __name__ == "__main__":
    test_development_project_root()
    print(
        "PASS: Development mode uses ~/InvestmentAnalyzer."
    )

    test_packaged_project_root()
    print(
        "PASS: Packaged mode uses ~/!InvestmentAnalyzer."
    )

    print("PASS: Path-selection tests completed.")
