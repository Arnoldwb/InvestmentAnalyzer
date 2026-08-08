"""
Read-only client for the Tiingo End-of-Day API.
"""

import json
import os
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from investment_analyzer.core.paths import PROJECT_ROOT


class TiingoError(Exception):
    """Raised when a Tiingo API request fails."""


class TiingoClient:
    """
    Retrieve security metadata and historical prices from Tiingo.

    This class is read-only. It does not create, modify, or remove
    Investment Analyzer fund data files.
    """

    BASE_URL = "https://api.tiingo.com/tiingo/daily"

    def __init__(self, token: str | None = None):
        self.token = token or self._load_token()

        if not self.token:
            raise TiingoError(
                "Tiingo API token was not found."
            )

    @staticmethod
    def _load_token() -> str:
        """
        Load the token from the environment or local .env file.
        """

        token = os.environ.get(
            "TIINGO_API_TOKEN",
            "",
        ).strip()

        if token:
            return token

        env_path = PROJECT_ROOT / ".env"

        if not env_path.exists():
            return ""

        for line in env_path.read_text().splitlines():
            line = line.strip()

            if (
                not line
                or line.startswith("#")
                or "=" not in line
            ):
                continue

            name, value = line.split("=", 1)

            if name.strip() == "TIINGO_API_TOKEN":
                return value.strip()

        return ""

    def _request(self, url: str):
        request = Request(
            url,
            headers={
                "Authorization": f"Token {self.token}",
                "Accept": "application/json",
                "User-Agent": "InvestmentAnalyzer/5.13",
            },
        )

        try:
            with urlopen(
                request,
                timeout=20,
            ) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except HTTPError as error:
            try:
                detail = json.loads(
                    error.read().decode("utf-8")
                ).get("detail", "")
            except Exception:
                detail = ""

            message = detail or (
                f"Tiingo returned HTTP {error.code}."
            )

            raise TiingoError(message) from error

        except URLError as error:
            raise TiingoError(
                f"Unable to contact Tiingo: {error.reason}"
            ) from error

        except json.JSONDecodeError as error:
            raise TiingoError(
                "Tiingo returned invalid JSON data."
            ) from error

    def get_metadata(self, symbol: str) -> dict:
        """
        Return Tiingo metadata for a ticker symbol.
        """

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Fund symbol cannot be empty."
            )

        return self._request(
            f"{self.BASE_URL}/{symbol}"
        )

    def get_prices(
        self,
        symbol: str,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
    ) -> list[dict]:
        """
        Return Tiingo daily price records for a ticker.
        """

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Fund symbol cannot be empty."
            )

        parameters = {}

        if start_date is not None:
            parameters["startDate"] = str(start_date)

        if end_date is not None:
            parameters["endDate"] = str(end_date)

        url = f"{self.BASE_URL}/{symbol}/prices"

        if parameters:
            url += "?" + urlencode(parameters)

        data = self._request(url)

        if not isinstance(data, list):
            raise TiingoError(
                "Tiingo returned an unexpected price response."
            )

        return data
