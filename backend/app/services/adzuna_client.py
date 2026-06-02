import json
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from app.config import settings


@dataclass
class AdzunaSearchParams:
    keyword: str
    location: str
    country: str
    page: int = 1
    results_per_page: int = 20


class AdzunaClient:
    base_url = "https://api.adzuna.com/v1/api/jobs"

    def search_jobs(self, params: AdzunaSearchParams) -> list[dict[str, Any]]:
        if not settings.adzuna_app_id or not settings.adzuna_app_key:
            raise ValueError("Adzuna credentials are not configured.")

        query = urlencode(
            {
                "app_id": settings.adzuna_app_id,
                "app_key": settings.adzuna_app_key,
                "what": params.keyword,
                "where": params.location,
                "results_per_page": params.results_per_page,
            }
        )
        url = f"{self.base_url}/{params.country}/search/{params.page}?{query}"

        try:
            with urlopen(url, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise RuntimeError(f"Adzuna request failed with status {error.code}.") from error
        except URLError as error:
            raise RuntimeError("Adzuna request could not reach the API.") from error

        results = payload.get("results", [])
        if not isinstance(results, list):
            raise RuntimeError("Adzuna response did not include a valid results list.")

        return results


def parse_adzuna_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass

    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
