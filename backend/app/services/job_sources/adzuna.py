import json
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from app.config import settings
from app.services.job_sources.base import (
    JobFetchParams,
    JobSource,
    JobSourceConfigurationError,
    JobSourceError,
    NormalizedJob,
)


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


class AdzunaJobSource(JobSource):
    source_name = "adzuna"
    base_url = "https://api.adzuna.com/v1/api/jobs"

    def fetch_jobs(self, params: JobFetchParams) -> list[NormalizedJob]:
        if not settings.adzuna_app_id or not settings.adzuna_app_key:
            raise JobSourceConfigurationError("Adzuna credentials are not configured.")

        query = urlencode(
            {
                "app_id": settings.adzuna_app_id,
                "app_key": settings.adzuna_app_key,
                "what": params.keyword,
                "where": params.location,
                "results_per_page": params.results_per_page,
            }
        )
        url = f"{self.base_url}/{params.country.lower()}/search/{params.page}?{query}"

        try:
            with urlopen(url, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise JobSourceError(f"Adzuna request failed with status {error.code}.") from error
        except URLError as error:
            raise JobSourceError("Adzuna request could not reach the API.") from error

        results = payload.get("results", [])
        if not isinstance(results, list):
            raise JobSourceError("Adzuna response did not include a valid results list.")

        jobs: list[NormalizedJob] = []
        for raw_job in results:
            company = raw_job.get("company") or {}
            location = raw_job.get("location") or {}
            jobs.append(
                NormalizedJob(
                    source=self.source_name,
                    external_id=str(raw_job["id"]),
                    title=raw_job.get("title") or "Untitled role",
                    company=company.get("display_name"),
                    location=location.get("display_name"),
                    remote_type=None,
                    salary_min=int(raw_job["salary_min"]) if raw_job.get("salary_min") is not None else None,
                    salary_max=int(raw_job["salary_max"]) if raw_job.get("salary_max") is not None else None,
                    description=raw_job.get("description"),
                    url=raw_job.get("redirect_url"),
                    posted_at=parse_adzuna_datetime(raw_job.get("created")),
                )
            )

        return jobs
