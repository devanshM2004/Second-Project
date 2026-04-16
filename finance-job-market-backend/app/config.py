"""Application configuration loaded from environment variables.

All secrets and environment-specific values should live here so that the rest
of the codebase imports a single settings object instead of reading os.environ
directly.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load variables from a local .env file if one exists. In production the
# environment is expected to provide these directly.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    bls_api_url: str
    bls_api_key: str | None

    @property
    def has_bls_key(self) -> bool:
        """Return True when a BLS registration key is configured."""
        return bool(self.bls_api_key)


def _get_env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if value else default


def load_settings() -> Settings:
    """Read environment variables and build a Settings object."""
    return Settings(
        app_name=_get_env("APP_NAME", "finance-job-market-backend"),
        app_env=_get_env("APP_ENV", "development"),
        bls_api_url=_get_env(
            "BLS_API_URL",
            "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        ),
        bls_api_key=_get_env("BLS_API_KEY") or None,
    )


# A single module-level settings instance keeps imports simple elsewhere.
settings = load_settings()
