# Finance Job Market Backend

A Python/FastAPI backend service that tracks the US job market for **entry-level finance roles**. This is a standalone, production-ready backend designed to aggregate live labor-market data from multiple sources. The first integrated data source is the **U.S. Bureau of Labor Statistics (BLS) Public Data API v2**.

---

## Why BLS Data?

The BLS is the gold standard for US labor market data. It publishes:

- **JOLTS** (Job Openings and Labor Turnover Survey) — monthly job openings, hires, and separations by sector
- **CES** (Current Employment Statistics) — total nonfarm payroll employment
- **LAUS** (Local Area Unemployment Statistics) — state and metro-level unemployment rates
- **OES** (Occupational Employment and Wage Statistics) — wages and employment by occupation

For a finance job market tracker, BLS data tells you *how many* finance jobs exist and what they pay at a macro level. Future data sources (Adzuna, USAJOBS, Greenhouse, etc.) will add real job listings to match against.

---

## Project Structure

```
finance-job-market-backend/
├── app/
│   ├── __init__.py          # Package metadata
│   ├── main.py              # FastAPI app factory and entry point
│   ├── config.py            # Environment variable loading via python-dotenv
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py        # GET /health
│   │   └── bls.py           # GET|POST /api/bls/...
│   ├── services/
│   │   ├── __init__.py
│   │   └── bls_service.py   # All BLS API logic lives here
│   ├── models/
│   │   ├── __init__.py
│   │   └── bls_models.py    # Pydantic request/response schemas
│   └── utils/
│       └── __init__.py      # Shared helpers (reserved for future use)
├── tests/
│   ├── __init__.py
│   ├── test_health.py       # Health endpoint tests
│   └── test_bls.py          # BLS service + route tests (mocked HTTP)
├── .env.example             # Template — copy to .env and fill in values
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Clone and enter the project

```bash
git clone https://github.com/<your-username>/finance-job-market-backend.git
cd finance-job-market-backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and edit as needed:

```env
APP_NAME=finance-job-market-backend
APP_ENV=development
BLS_API_URL=https://api.bls.gov/publicAPI/v2/timeseries/data/
BLS_API_KEY=          # optional — see below
```

> **BLS API Key** — The app works without a key in basic mode (limited to ~25 requests per day per IP, max 10 series per request, and no `catalog`/`calculations` flags). Register for free at [data.bls.gov/registrationEngine](https://data.bls.gov/registrationEngine/) to get a key that lifts these limits.

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

### 6. Run tests

```bash
pytest
```

---

## API Reference

### `GET /health`

Confirms the service is running.

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "app": "finance-job-market-backend",
  "env": "development",
  "bls_api_key_configured": false
}
```

---

### `GET /api/bls/series/{series_id}`

Fetch observations for a single BLS series.

| Query param | Type | Required | Description |
|---|---|---|---|
| `start_year` | int | No | Earliest year to include |
| `end_year` | int | No | Latest year to include |

```bash
# Unemployment rate — seasonally adjusted (LNS14000000)
curl "http://localhost:8000/api/bls/series/LNS14000000?start_year=2022&end_year=2024"
```

```json
{
  "status": "ok",
  "series_count": 1,
  "data": [
    {
      "series_id": "LNS14000000",
      "year": "2024",
      "period": "M01",
      "period_name": "January",
      "value": 3.7,
      "footnotes": ["Preliminary"]
    }
  ]
}
```

---

### `POST /api/bls/series`

Fetch multiple series in one request.

```bash
curl -X POST http://localhost:8000/api/bls/series \
  -H "Content-Type: application/json" \
  -d '{
    "series_ids": ["LNS14000000", "CES0000000001"],
    "start_year": 2022,
    "end_year": 2024,
    "calculations": false,
    "annualaverage": false
  }'
```

**Request body schema:**

| Field | Type | Required | Description |
|---|---|---|---|
| `series_ids` | list[str] | Yes | 1–50 BLS series IDs |
| `start_year` | int | Yes | Start of date range |
| `end_year` | int | Yes | End of date range (≥ start_year) |
| `catalog` | bool | No | Include BLS catalog metadata (requires API key) |
| `calculations` | bool | No | Include net/percent changes (requires API key) |
| `annualaverage` | bool | No | Include annual averages (requires API key) |

---

### `GET /api/bls/jolts`

Returns JOLTS job openings data. Defaults to total nonfarm job openings (`JTS000000000000000JOL`).

```bash
curl "http://localhost:8000/api/bls/jolts?start_year=2022&end_year=2024"
```

Override the series with any valid JOLTS ID:

```bash
curl "http://localhost:8000/api/bls/jolts?series_id=JTS230000000000000JOL&start_year=2023&end_year=2024"
```

---

## Useful BLS Series IDs

| Series ID | Description |
|---|---|
| `LNS14000000` | Unemployment rate, seasonally adjusted |
| `CES0000000001` | Total nonfarm payroll employment |
| `CES5500000001` | Financial activities employment |
| `CES5552000001` | Finance and insurance employment |
| `JTS000000000000000JOL` | JOLTS — total nonfarm job openings |
| `JTS520000000000000JOL` | JOLTS — finance & insurance job openings |
| `OEUN000000000000520000010` | OES — financial analysts, mean wage |

---

## Future Expansion Ideas

This backend is designed to grow. Planned integrations and features:

| Source | What it adds |
|---|---|
| **Adzuna API** | Live entry-level finance job postings with salary bands |
| **USAJOBS API** | Federal government finance and accounting roles |
| **O\*NET API** | Skill requirements and career pathway data for finance occupations |
| **Greenhouse API** | Real-time job board postings from fintech companies |
| **Lever API** | Additional company-level hiring signals |
| **Job classification engine** | NLP-based tagger to classify roles as entry/mid/senior and map them to BLS occupation codes |
| **Trend analytics** | Month-over-month and year-over-year change calculations on top of BLS data |
| **PostgreSQL + SQLAlchemy** | Persist fetched data so dashboards can query historical snapshots |
| **Background scheduler (APScheduler)** | Automatically refresh BLS and job board data on a cron schedule |
| **Authentication** | API key middleware to expose data to a frontend or third-party consumers |

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `finance-job-market-backend` | Shown in health check and API metadata |
| `APP_ENV` | `development` | Environment label (`development` / `production`) |
| `BLS_API_URL` | `https://api.bls.gov/publicAPI/v2/timeseries/data/` | BLS v2 endpoint |
| `BLS_API_KEY` | *(empty)* | Optional BLS registration key |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| HTTP client | [requests](https://requests.readthedocs.io/) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Config | [python-dotenv](https://github.com/theskumar/python-dotenv) |
| Testing | [pytest](https://docs.pytest.org/) + [httpx](https://www.python-httpx.org/) |

---

## License

MIT
