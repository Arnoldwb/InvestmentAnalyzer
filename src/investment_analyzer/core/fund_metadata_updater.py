import json

from investment_analyzer.core.fund_metadata import METADATA_FILE
from investment_analyzer.core.paths import DATA_DIR
from investment_analyzer.core.tiingo_client import TiingoClient


class FundMetadataUpdater:
    """
    Populate and update local fund-name metadata from Tiingo.
    """

    def __init__(self, client=None):
        self.client = client or TiingoClient()

    def load_metadata(self):
        """
        Load the existing local metadata.
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

    def save_metadata(self, metadata):
        """
        Save metadata to the local metadata file.
        """

        METADATA_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with METADATA_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                metadata,
                file,
                indent=4,
                sort_keys=True,
            )

            file.write("\n")

    def update_all(self):
        """
        Add missing fund names for all CSV files in DATA_DIR.

        Existing metadata entries are preserved.
        """

        metadata = self.load_metadata()

        symbols = sorted(
            path.stem.strip().upper()
            for path in DATA_DIR.glob("*.csv")
            if path.stem.strip()
        )

        added = []
        skipped = []
        failed = []

        for symbol in symbols:
            if symbol in metadata:
                skipped.append(symbol)
                continue

            try:
                info = self.client.get_metadata(symbol)
                name = str(info.get("name", "")).strip()

                if not name:
                    failed.append((symbol, "Tiingo returned no fund name."))
                    continue

                metadata[symbol] = {
                    "name": name,
                }

                added.append(symbol)

            except Exception as error:
                failed.append((symbol, str(error)))

        self.save_metadata(metadata)

        return {
            "added": added,
            "skipped": skipped,
            "failed": failed,
        }
