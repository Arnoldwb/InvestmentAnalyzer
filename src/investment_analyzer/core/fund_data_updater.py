"""
Automatic fund-data updates from Tiingo.

Updates preserve existing historical rows and append only dates
later than the fund's latest usable date.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import shutil

import pandas as pd

from investment_analyzer.core.fund_data_validator import (
    FundDataValidator,
    ValidationResult,
)
from investment_analyzer.core.paths import (
    DATA_BACKUP_DIR,
    DATA_DIR,
)
from investment_analyzer.core.tiingo_client import TiingoClient


@dataclass
class UpdatePreview:
    """Summary of a prospective Tiingo fund-data update."""

    symbol: str
    current_last_date: pd.Timestamp
    tiingo_last_date: pd.Timestamp | None
    new_rows: int
    prices: list[dict]

    @property
    def update_available(self) -> bool:
        return self.new_rows > 0


@dataclass
class UpdateResult:
    """Result of applying a Tiingo fund-data update."""

    symbol: str
    updated: bool
    rows_added: int
    destination: Path
    backup: Path | None
    validation: ValidationResult | None


class FundDataUpdater:
    """
    Preview and safely apply Tiingo fund-data updates.
    """

    def __init__(
        self,
        client: TiingoClient | None = None,
        data_dir: Path | None = None,
        backup_dir: Path | None = None,
    ):
        self.client = client or TiingoClient()

        self.data_dir = (
            Path(data_dir)
            if data_dir is not None
            else DATA_DIR
        )

        self.backup_dir = (
            Path(backup_dir)
            if backup_dir is not None
            else DATA_BACKUP_DIR
        )

        self.validator = FundDataValidator()

    def _fund_path(self, symbol: str) -> Path:
        return self.data_dir / f"{symbol}.csv"

    def _load_existing(self, symbol: str) -> pd.DataFrame:
        path = self._fund_path(symbol)

        if not path.exists():
            raise FileNotFoundError(path)

        data = pd.read_csv(path)

        data.columns = [
            str(column).strip()
            for column in data.columns
        ]

        if "Date" not in data.columns:
            raise ValueError(
                f"{symbol} does not contain a Date column."
            )

        if "Adj Close" not in data.columns:
            raise ValueError(
                f"{symbol} does not contain an Adj Close column."
            )

        parsed_dates = pd.to_datetime(
            data["Date"],
            format="%d-%b-%y",
            errors="coerce",
        )

        unresolved = parsed_dates.isna() & data["Date"].notna()

        if unresolved.any():
            parsed_dates.loc[unresolved] = pd.to_datetime(
                data.loc[unresolved, "Date"],
                format="mixed",
                errors="coerce",
            )

        adjusted = pd.to_numeric(
            data["Adj Close"],
            errors="coerce",
        )

        usable = (
            parsed_dates.notna()
            & adjusted.notna()
        )

        clean = data.loc[usable].copy()
        clean["_parsed_date"] = parsed_dates.loc[usable]

        clean = clean.sort_values(
            "_parsed_date"
        ).reset_index(drop=True)

        return clean

    def preview_update(self, symbol: str) -> UpdatePreview:
        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Fund symbol cannot be empty."
            )

        existing = self._load_existing(symbol)

        if existing.empty:
            raise ValueError(
                f"{symbol} contains no usable historical data."
            )

        current_last_date = pd.Timestamp(
            existing["_parsed_date"].iloc[-1]
        ).normalize()

        start_date = (
            current_last_date
            + timedelta(days=1)
        ).date()

        metadata = self.client.get_metadata(symbol)

        tiingo_end = metadata.get("endDate")

        tiingo_last_date = (
            pd.Timestamp(tiingo_end).normalize()
            if tiingo_end
            else None
        )

        if (
            tiingo_last_date is None
            or tiingo_last_date <= current_last_date
        ):
            return UpdatePreview(
                symbol=symbol,
                current_last_date=current_last_date,
                tiingo_last_date=tiingo_last_date,
                new_rows=0,
                prices=[],
            )

        prices = self.client.get_prices(
            symbol,
            start_date=start_date,
            end_date=tiingo_last_date.date(),
        )

        new_prices = []

        for row in prices:
            row_date = pd.Timestamp(
                row["date"]
            ).tz_localize(None).normalize()

            if row_date > current_last_date:
                new_prices.append(row)

        return UpdatePreview(
            symbol=symbol,
            current_last_date=current_last_date,
            tiingo_last_date=tiingo_last_date,
            new_rows=len(new_prices),
            prices=new_prices,
        )

    @staticmethod
    def _tiingo_rows(prices: list[dict]) -> pd.DataFrame:
        rows = []

        for item in prices:
            row_date = pd.Timestamp(
                item["date"]
            ).tz_localize(None)

            rows.append(
                {
                    "Date": row_date.strftime("%d-%b-%y"),
                    "Open": item.get("open"),
                    "High": item.get("high"),
                    "Low": item.get("low"),
                    "Close": item.get("close"),
                    "Adj Close": item.get("adjClose"),
                    "Volume": (
                        item.get("volume")
                        if item.get("volume") not in (None, 0)
                        else "-"
                    ),
                    "_parsed_date": row_date.normalize(),
                }
            )

        return pd.DataFrame(rows)

    def apply_update(
        self,
        symbol: str,
        preview: UpdatePreview | None = None,
    ) -> UpdateResult:
        """
        Safely append newer Tiingo rows to an existing fund CSV.

        A complete staged CSV is validated before the original file
        is backed up and atomically replaced.
        """

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Fund symbol cannot be empty."
            )

        destination = self._fund_path(symbol)

        if preview is None:
            preview = self.preview_update(symbol)

        if preview.symbol != symbol:
            raise ValueError(
                "Update preview does not match the requested symbol."
            )

        if not preview.update_available:
            return UpdateResult(
                symbol=symbol,
                updated=False,
                rows_added=0,
                destination=destination,
                backup=None,
                validation=None,
            )

        existing = self._load_existing(symbol)
        new_data = self._tiingo_rows(preview.prices)

        columns = [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume",
        ]

        for column in columns:
            if column not in existing.columns:
                existing[column] = ""

        merged = pd.concat(
            [
                existing[columns + ["_parsed_date"]],
                new_data[columns + ["_parsed_date"]],
            ],
            ignore_index=True,
        )

        merged = (
            merged
            .sort_values("_parsed_date")
            .drop_duplicates(
                subset="_parsed_date",
                keep="first",
            )
            .reset_index(drop=True)
        )

        staging = self.data_dir / (
            f".{symbol}.updating.csv"
        )

        staging.unlink(missing_ok=True)

        try:
            merged[columns].to_csv(
                staging,
                index=False,
            )

            validation = self.validator.validate(
                staging
            )

            if not validation.valid:
                details = "; ".join(
                    validation.errors
                )

                raise ValueError(
                    "Updated fund data failed validation: "
                    + details
                )

            self.backup_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            timestamp = datetime.now().strftime(
                "%Y-%m-%d_%H%M%S"
            )

            backup = self.backup_dir / (
                f"{symbol}_{timestamp}.csv"
            )

            shutil.copy2(
                destination,
                backup,
            )

            staging.replace(destination)

        finally:
            staging.unlink(missing_ok=True)

        installed_validation = self.validator.validate(
            destination
        )

        return UpdateResult(
            symbol=symbol,
            updated=True,
            rows_added=preview.new_rows,
            destination=destination,
            backup=backup,
            validation=installed_validation,
        )
