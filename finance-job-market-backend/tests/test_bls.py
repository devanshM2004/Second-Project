"""Tests for the BLS service and routes using mocked HTTP responses."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.bls_service import BLSService, BLSServiceError

client = TestClient(app)


SAMPLE_BLS_RESPONSE = {
    "status": "REQUEST_SUCCEEDED",
    "responseTime": 42,
    "message": [],
    "Results": {
        "series": [
            {
                "seriesID": "LNS14000000",
                "data": [
                    {
                        "year": "2024",
                        "period": "M01",
                        "periodName": "January",
                        "value": "3.7",
                        "footnotes": [{"code": "P", "text": "Preliminary"}],
                    },
                    {
                        "year": "2023",
                        "period": "M12",
                        "periodName": "December",
                        "value": "3.5",
                        "footnotes": [{}],
                    },
                ],
            }
        ]
    },
}


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


def test_service_normalizes_response():
    service = BLSService(api_key=None)

    with patch("app.services.bls_service.requests.post") as mock_post:
        mock_post.return_value = _FakeResponse(SAMPLE_BLS_RESPONSE)
        data = service.fetch_single_series("LNS14000000", 2023, 2024)

    assert len(data) == 2
    first = data[0]
    assert first.series_id == "LNS14000000"
    assert first.year == "2024"
    assert first.period == "M01"
    assert first.period_name == "January"
    assert first.value == 3.7
    assert first.footnotes == ["Preliminary"]


def test_service_raises_on_bls_error_status():
    service = BLSService(api_key=None)
    bad_payload = {"status": "REQUEST_NOT_PROCESSED", "message": ["bad series"]}

    with patch("app.services.bls_service.requests.post") as mock_post:
        mock_post.return_value = _FakeResponse(bad_payload)
        try:
            service.fetch_single_series("BOGUS", 2023, 2024)
        except BLSServiceError as err:
            assert "bad series" in err.message
        else:
            raise AssertionError("Expected BLSServiceError")


def test_get_single_series_route_with_mock():
    with patch(
        "app.routes.bls.bls_service.fetch_single_series"
    ) as mock_fetch:
        mock_fetch.return_value = [
            # Return already-normalized data points
            __import__(
                "app.models.bls_models", fromlist=["BLSDataPoint"]
            ).BLSDataPoint(
                series_id="LNS14000000",
                year="2024",
                period="M01",
                period_name="January",
                value=3.7,
                footnotes=["Preliminary"],
            )
        ]

        response = client.get("/api/bls/series/LNS14000000?start_year=2024&end_year=2024")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["series_count"] == 1
    assert body["data"][0]["series_id"] == "LNS14000000"
    assert body["data"][0]["value"] == 3.7


def test_post_multi_series_route_with_mock():
    payload = {
        "series_ids": ["LNS14000000", "CES0000000001"],
        "start_year": 2023,
        "end_year": 2024,
    }

    with patch("app.routes.bls.bls_service.fetch_series") as mock_fetch:
        mock_fetch.return_value = [
            __import__(
                "app.models.bls_models", fromlist=["BLSDataPoint"]
            ).BLSDataPoint(
                series_id="LNS14000000",
                year="2024",
                period="M01",
                period_name="January",
                value=3.7,
                footnotes=[],
            )
        ]
        response = client.post("/api/bls/series", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["series_count"] == 2
    assert body["data"][0]["series_id"] == "LNS14000000"


def test_post_multi_series_rejects_bad_year_range():
    payload = {
        "series_ids": ["LNS14000000"],
        "start_year": 2024,
        "end_year": 2020,
    }
    response = client.post("/api/bls/series", json=payload)
    assert response.status_code == 422
