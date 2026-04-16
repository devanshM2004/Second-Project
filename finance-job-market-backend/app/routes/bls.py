"""BLS routes: single-series GET, multi-series POST, and a JOLTS helper."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.bls_models import (
    BLSSeriesRequest,
    BLSSeriesResponse,
)
from app.services.bls_service import (
    DEFAULT_JOLTS_SERIES_ID,
    BLSServiceError,
    bls_service,
)

router = APIRouter()


def _raise_http(err: BLSServiceError) -> None:
    """Translate a service-level error into a FastAPI HTTPException."""
    raise HTTPException(status_code=err.status_code, detail=err.message)


@router.get("/series/{series_id}", response_model=BLSSeriesResponse)
def get_single_series(
    series_id: str,
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
) -> BLSSeriesResponse:
    """Fetch a single BLS series by ID."""
    if end_year is not None and start_year is not None and end_year < start_year:
        raise HTTPException(
            status_code=400,
            detail="end_year must be greater than or equal to start_year",
        )

    try:
        data = bls_service.fetch_single_series(
            series_id=series_id,
            start_year=start_year,
            end_year=end_year,
        )
    except BLSServiceError as err:
        _raise_http(err)

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No data returned for series '{series_id}'",
        )

    return BLSSeriesResponse(
        status="ok",
        series_count=1,
        data=data,
    )


@router.post("/series", response_model=BLSSeriesResponse)
def post_multi_series(request: BLSSeriesRequest) -> BLSSeriesResponse:
    """Fetch one or more BLS series in a single request."""
    try:
        data = bls_service.fetch_series(
            series_ids=request.series_ids,
            start_year=request.start_year,
            end_year=request.end_year,
            catalog=request.catalog,
            calculations=request.calculations,
            annualaverage=request.annualaverage,
        )
    except BLSServiceError as err:
        _raise_http(err)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="BLS returned no observations for the requested series",
        )

    return BLSSeriesResponse(
        status="ok",
        series_count=len(request.series_ids),
        data=data,
    )


@router.get("/jolts", response_model=BLSSeriesResponse)
def get_jolts(
    series_id: str = Query(
        DEFAULT_JOLTS_SERIES_ID,
        description="Override the default JOLTS series ID if desired.",
    ),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
) -> BLSSeriesResponse:
    """Return JOLTS data. Defaults to total nonfarm job openings."""
    try:
        data = bls_service.fetch_single_series(
            series_id=series_id,
            start_year=start_year,
            end_year=end_year,
        )
    except BLSServiceError as err:
        _raise_http(err)

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No JOLTS data returned for series '{series_id}'",
        )

    return BLSSeriesResponse(
        status="ok",
        message="JOLTS data retrieved from BLS",
        series_count=1,
        data=data,
    )
