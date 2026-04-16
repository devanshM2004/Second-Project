"""Pydantic request/response models for BLS endpoints."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class BLSSeriesRequest(BaseModel):
    """Incoming request body for POST /api/bls/series.

    Mirrors the BLS Public Data API v2 payload shape but is validated on our
    side before it leaves the backend.
    """

    series_ids: List[str] = Field(
        ...,
        description="One or more BLS series IDs to fetch.",
        min_length=1,
        max_length=50,
    )
    start_year: int = Field(..., ge=1900, le=2100)
    end_year: int = Field(..., ge=1900, le=2100)

    # Optional BLS flags
    catalog: bool = False
    calculations: bool = False
    annualaverage: bool = False

    @field_validator("series_ids")
    @classmethod
    def strip_series_ids(cls, ids: List[str]) -> List[str]:
        cleaned = [s.strip() for s in ids if s and s.strip()]
        if not cleaned:
            raise ValueError("series_ids must contain at least one non-empty value")
        return cleaned

    @field_validator("end_year")
    @classmethod
    def end_after_start(cls, end_year: int, info) -> int:
        start_year = info.data.get("start_year")
        if start_year is not None and end_year < start_year:
            raise ValueError("end_year must be greater than or equal to start_year")
        return end_year


class BLSDataPoint(BaseModel):
    """Normalized, flattened representation of a single BLS observation."""

    series_id: str
    year: str
    period: str
    period_name: str
    value: Optional[float]
    footnotes: List[str] = Field(default_factory=list)


class BLSSeriesResponse(BaseModel):
    """Response envelope returned to API consumers."""

    status: str
    message: Optional[str] = None
    series_count: int
    data: List[BLSDataPoint]
