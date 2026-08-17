from dataclasses import dataclass, field
from io import StringIO

import pandas as pd


@dataclass
class ClipboardParseResult:
    """
    Result of parsing copied historical price data.
    """

    valid: bool = False
    rows_received: int = 0
    usable_rows: int = 0
    ignored_rows: int = 0
    data: pd.DataFrame = field(
        default_factory=pd.DataFrame
    )
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class FundClipboardParser:
    """
    Parse historical price data copied from Yahoo Finance.

    The parser does not write files or modify the fund library.
    """

    REQUIRED_COLUMNS = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
    ]

    def parse(self, text: str) -> ClipboardParseResult:
        result = ClipboardParseResult()

        if not text or not text.strip():
            result.errors.append(
                "Clipboard does not contain historical data."
            )
            return result

        try:
            data = pd.read_csv(
                StringIO(text),
                sep=None,
                engine="python",
                dtype=str,
            )
        except Exception as error:
            result.errors.append(
                f"Unable to read clipboard data: {error}"
            )
            return result

        data.columns = [
            str(column).strip()
            for column in data.columns
        ]

        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in data.columns
        ]

        if missing:
            result.errors.append(
                "Missing required column(s): "
                + ", ".join(missing)
            )
            return result

        data = data[
            self.REQUIRED_COLUMNS
        ].copy()

        result.rows_received = len(data)

        parsed_dates = pd.to_datetime(
            data["Date"],
            format="mixed",
            errors="coerce",
        )

        numeric_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
        ]

        numeric_data = {}

        for column in numeric_columns:
            cleaned = (
                data[column]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
            )

            numeric_data[column] = pd.to_numeric(
                cleaned,
                errors="coerce",
            )

        usable = parsed_dates.notna()

        for column in numeric_columns:
            usable &= numeric_data[column].notna()

        usable &= numeric_data["Adj Close"] > 0

        # Detect obviously truncated or corrupted copied rows.
        #
        # Adjusted Close can legitimately differ from Close,
        # especially in older historical data. However, a very
        # large difference usually indicates that clipboard
        # selection ended partway through a value or row.
        close_values = numeric_data["Close"]
        adjusted_values = numeric_data["Adj Close"]

        comparable = (
            close_values.notna()
            & adjusted_values.notna()
            & (close_values > 0)
            & (adjusted_values > 0)
        )

        price_ratio = pd.Series(
            1.0,
            index=data.index,
        )

        price_ratio.loc[comparable] = (
            adjusted_values.loc[comparable]
            / close_values.loc[comparable]
        )

        suspicious_price = comparable & (
            (price_ratio < 0.25)
            | (price_ratio > 4.0)
        )

        usable &= ~suspicious_price

        if suspicious_price.any():
            count = int(suspicious_price.sum())

            result.warnings.append(
                f"{count} row(s) had an implausible "
                "Close / Adj Close relationship and "
                "were ignored as possibly incomplete "
                "clipboard data."
            )

        ignored = ~usable

        result.ignored_rows = int(
            ignored.sum()
        )

        if result.ignored_rows:
            result.warnings.append(
                f"{result.ignored_rows} incomplete or "
                "non-price row(s) were ignored."
            )

        clean = data.loc[usable].copy()

        if clean.empty:
            result.errors.append(
                "No usable historical price rows were found."
            )
            return result

        clean["Date"] = parsed_dates.loc[
            usable
        ].dt.strftime("%d-%b-%y")

        for column in numeric_columns:
            clean[column] = numeric_data[
                column
            ].loc[usable]

        clean["Volume"] = (
            clean["Volume"]
            .fillna("-")
            .astype(str)
            .str.strip()
        )

        clean = clean.sort_values(
            "Date",
            key=lambda values: pd.to_datetime(
                values,
                format="%d-%b-%y",
            ),
        ).reset_index(drop=True)

        result.usable_rows = len(clean)
        result.data = clean
        result.valid = True

        if result.usable_rows < 24:
            result.warnings.append(
                f"Only {result.usable_rows} usable row(s) "
                "were copied. Investment Analyzer requires "
                "at least 24 rows for an importable fund."
            )

        return result
