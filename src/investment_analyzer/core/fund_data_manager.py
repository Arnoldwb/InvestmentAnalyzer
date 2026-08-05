from dataclasses import dataclass
from pathlib import Path
import shutil

from investment_analyzer.core.fund_data_validator import (
    FundDataValidator,
    ValidationResult,
)
from investment_analyzer.core.fund_library import FundLibrary
from investment_analyzer.core.paths import (
    DATA_DIR,
    PORTFOLIO_DIR,
)


@dataclass
class ImportResult:
    """
    Result of importing a fund CSV.
    """

    source: Path
    destination: Path | None
    validation: ValidationResult
    imported: bool = False
    replaced: bool = False


@dataclass
class RemoveResult:
    """
    Result of removing a fund CSV.
    """

    symbol: str
    path: Path | None
    removed: bool = False


class FundDataManager:
    """
    Safely import, validate, replace, and remove fund data.
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

        self.data_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.portfolio_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.validator = FundDataValidator()

    def _library(self) -> FundLibrary:
        return FundLibrary(
            data_dir=self.data_dir,
            portfolio_dir=self.portfolio_dir,
        )

    def validate_file(
        self,
        filename,
    ) -> ValidationResult:
        """
        Validate a CSV without importing it.
        """

        return self.validator.validate(filename)

    def validate_all(self) -> list[ValidationResult]:
        """
        Validate every CSV in the fund library.
        """

        return [
            self.validator.validate(path)
            for path in sorted(
                self.data_dir.glob("*.csv")
            )
        ]

    def import_file(
        self,
        filename,
        replace: bool = False,
    ) -> ImportResult:
        """
        Validate and import a fund CSV.

        Existing files are never overwritten unless
        replace=True. Replacements are staged and validated
        before the existing file is changed.
        """

        source = Path(filename)
        validation = self.validator.validate(source)

        result = ImportResult(
            source=source,
            destination=None,
            validation=validation,
        )

        if not validation.valid:
            return result

        symbol = validation.symbol
        destination = self.data_dir / f"{symbol}.csv"

        result.destination = destination

        if destination.exists() and not replace:
            raise FileExistsError(
                f"{symbol} already exists in the fund library."
            )

        try:
            same_file = (
                source.resolve()
                == destination.resolve()
            )
        except OSError:
            same_file = False

        if same_file:
            result.imported = True
            return result

        destination_existed = destination.exists()

        staging = self.data_dir / (
            f".{symbol}.importing.csv"
        )

        staging.unlink(missing_ok=True)

        try:
            shutil.copy2(
                source,
                staging,
            )

            staged_validation = self.validator.validate(
                staging
            )

            if not staged_validation.valid:
                raise ValueError(
                    "Imported file failed validation "
                    "after copying."
                )

            staging.replace(destination)

        finally:
            staging.unlink(missing_ok=True)

        installed_validation = self.validator.validate(
            destination
        )

        result.validation = installed_validation
        result.imported = True
        result.replaced = destination_existed

        return result

    def remove_fund(
        self,
        symbol: str,
    ) -> RemoveResult:
        """
        Remove an unused fund CSV.

        Funds referenced by saved portfolios cannot
        be removed.
        """

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Fund symbol cannot be empty."
            )

        path = self.data_dir / f"{symbol}.csv"

        if not path.exists():
            raise FileNotFoundError(
                f"Fund data file not found: {path}"
            )

        used_by = self._library().portfolios_using(
            symbol
        )

        if used_by:
            portfolio_list = ", ".join(used_by)

            raise ValueError(
                f"{symbol} cannot be removed because it is "
                f"used by: {portfolio_list}"
            )

        path.unlink()

        return RemoveResult(
            symbol=symbol,
            path=path,
            removed=True,
        )
