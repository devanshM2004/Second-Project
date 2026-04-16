"""BLS Public Data API v2 integration.

This module owns every interaction with api.bls.gov. Keeping the HTTP logic
out of the route handlers makes it trivial to mock in tests and to extend
later with caching or retry behavior.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from app.config import settings
from app.models.bls_models import BLSDataPoint


class BLSServiceError(Exception):
    """Raised when the BLS API returns an error or cannot be reached."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# Default JOLTS series: Job Openings, Total Nonfarm (seasonally adjusted).
# See https://www.bls.gov/help/hlpforma.htm#JT
DEFAULT_JOLTS_SERIES_ID = "JTS000000000000000JOL"


class BLSService:
    """Thin wrapper around the BLS Public Data API v2."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = base_url or settings.bls_api_url
        self.api_key = api_key if api_key is not None else settings.bls_api_key
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
    def fetch_single_series(
        self,
        series_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> List[BLSDataPoint]:
        """Fetch a single series. Convenience wrapper around fetch_series."""
        if not series_id or not series_id.strip():
            raise BLSServiceError("series_id must be a non-empty string", 400)

        return self.fetch_series(
            series_ids=[series_id.strip()],
            start_year=start_year,
            end_year=end_year,
        )

    def fetch_series(
        self,
        series_ids: List[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        catalog: bool = False,
        calculations: bool = False,
        annualaverage: bool = False,
    ) -> List[BLSDataPoint]:
        """Fetch one or more series from the BLS API and normalize the result."""
        if not series_ids:
            raise BLSServiceError("At least one series_id is required", 400)

        payload = self._build_payload(
            series_ids=series_ids,
            start_year=start_year,
            end_year=end_year,
            catalog=catalog,
            calculations=calculations,
            annualaverage=annualaverage,
        )

        raw = self._post(payload)
        self._validate_response(raw)
        return self._normalize(raw)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_payload(
        self,
        series_ids: List[str],
        start_year: Optional[int],
        end_year: Optional[int],
        catalog: bool,
        calculations: bool,
        annualaverage: bool,
    ) -> Dict[str, Any]:
        """Assemble the JSON body expected by the BLS v2 endpoint."""
        payload: Dict[str, Any] = {"seriesid": series_ids}

        if start_year is not None:
            payload["startyear"] = str(start_year)
        if end_year is not None:
            payload["endyear"] = str(end_year)

        # Optional flags only supported when a registration key is provided.
        if self.api_key:
            payload["registrationkey"] = self.api_key
            if catalog:
                payload["catalog"] = True
            if calculations:
                payload["calculations"] = True
            if annualaverage:
                payload["annualaverage"] = True

        return payload

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send the POST request and return the decoded JSON body."""
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
        except requests.Timeout as exc:
            raise BLSServiceError("BLS API request timed out", 504) from exc
        except requests.RequestException as exc:
            raise BLSServiceError(f"BLS API request failed: {exc}", 502) from exc

        if response.status_code >= 500:
            raise BLSServiceError(
                f"BLS API returned server error {response.status_code}", 502
            )
        if response.status_code >= 400:
            raise BLSServiceError(
                f"BLS API rejected the request ({response.status_code})", 400
            )

        try:
            return response.json()
        except ValueError as exc:
            raise BLSServiceError("BLS API returned invalid JSON", 502) from exc

    def _validate_response(self, data: Dict[str, Any]) -> None:
        """Ensure the BLS envelope looks like a successful response."""
        status = data.get("status")
        if status != "REQUEST_SUCCEEDED":
            messages = data.get("message") or ["Unknown BLS error"]
            joined = "; ".join(messages) if isinstance(messages, list) else str(messages)
            raise BLSServiceError(f"BLS API error: {joined}", 400)

        results = data.get("Results")
        if not isinstance(results, dict):
            raise BLSServiceError("BLS response missing 'Results' object", 502)

        if "series" not in results:
            raise BLSServiceError("BLS response missing 'series' payload", 502)

    def _normalize(self, data: Dict[str, Any]) -> List[BLSDataPoint]:
        """Flatten the BLS nested structure into a clean list of data points."""
        flattened: List[BLSDataPoint] = []

        for series in data["Results"]["series"]:
            series_id = series.get("seriesID", "")
            for obs in series.get("data", []):
                flattened.append(
                    BLSDataPoint(
                        series_id=series_id,
                        year=str(obs.get("year", "")),
                        period=str(obs.get("period", "")),
                        period_name=str(obs.get("periodName", "")),
                        value=_to_float(obs.get("value")),
                        footnotes=_clean_footnotes(obs.get("footnotes", [])),
                    )
                )

        return flattened


def _to_float(value: Any) -> Optional[float]:
    """Convert BLS string values to float; return None if unparseable."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_footnotes(raw: Any) -> List[str]:
    """BLS returns footnotes as a list of dicts with optional text fields."""
    if not isinstance(raw, list):
        return []
    notes: List[str] = []
    for item in raw:
        if isinstance(item, dict):
            text = item.get("text")
            if text:
                notes.append(str(text))
    return notes


# A default service instance used by routes. Tests can inject their own.
bls_service = BLSService()
