from dataclasses import dataclass, field
import json
from pathlib import Path

from investment_analyzer.core.fund_data_validator import (
    FundDataValidator,
    ValidationResult,
)
from investment_analyzer.core.paths import (
    DATA_DIR,
    PORTFOLIO_DIR,
)


@dataclass
class FundLibraryEntry:
    """
    Information about one fund in the Investment Analyzer
    data library.
    """

    symbol: str
    path: Path
    validation: ValidationResult
    used_by: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return self.validation.status

    @property
    def usable_rows(self) -> int:
        return self.validation.usable_rows

    @property
    def first_date(self):
        return self.validation.first_date

    @property
    def last_date(self):
        return self.validation.last_date

    @property
    def portfolio_count(self) -> int:
        return len(self.used_by)


class FundLibrary:
    """
    Inspect the Investment Analyzer fund-data library.
    """

    def __init__(
        self,
        data_dir: Path | None = None,
        portfolio_dir: Path | None = None,
    ):
        self.data_dir = (
            Path(data_dir)
            if data_dir is not None
            else DATA_DIR
        )

        self.portfolio_dir = (
            Path(portfolio_dir)
            if portfolio_dir is not None
            else PORTFOLIO_DIR
        )

        self.validator = FundDataValidator()

    def _portfolio_usage(self) -> dict[str, list[str]]:
        """
        Return a mapping of fund symbol to saved portfolios
        that reference the symbol.
        """

        usage: dict[str, list[str]] = {}

        if not self.portfolio_dir.exists():
            return usage

        for path in sorted(
            self.portfolio_dir.glob("*.json")
        ):
            try:
                with path.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    data = json.load(file)
            except (OSError, json.JSONDecodeError):
                # A damaged portfolio should not prevent the
                # fund library itself from being displayed.
                continue

            portfolio_name = (
                str(data.get("name", "")).strip()
                or path.stem
            )

            for holding in data.get(
                "holdings",
                [],
            ):
                symbol = str(
                    holding.get("symbol", "")
                ).strip().upper()

                if not symbol:
                    continue

                portfolios = usage.setdefault(
                    symbol,
                    [],
                )

                if portfolio_name not in portfolios:
                    portfolios.append(portfolio_name)

        return usage

    def entries(self) -> list[FundLibraryEntry]:
        """
        Return information for every CSV in the data library.
        """

        if not self.data_dir.exists():
            return []

        usage = self._portfolio_usage()

        entries = []

        for path in sorted(
            self.data_dir.glob("*.csv")
        ):
            validation = self.validator.validate(
                path
            )

            symbol = validation.symbol

            entries.append(
                FundLibraryEntry(
                    symbol=symbol,
                    path=path,
                    validation=validation,
                    used_by=usage.get(
                        symbol,
                        [],
                    ),
                )
            )

        return entries

    def get(self, symbol: str) -> FundLibraryEntry | None:
        """
        Return one fund-library entry by symbol.
        """

        symbol = symbol.strip().upper()

        for entry in self.entries():
            if entry.symbol == symbol:
                return entry

        return None

    def portfolios_using(
        self,
        symbol: str,
    ) -> list[str]:
        """
        Return saved portfolios that reference a fund.
        """

        symbol = symbol.strip().upper()

        return self._portfolio_usage().get(
            symbol,
            [],
        )
