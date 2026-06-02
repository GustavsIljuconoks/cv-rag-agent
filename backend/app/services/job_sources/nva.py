import json
import re
from datetime import datetime
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.services.job_sources.base import (
    JobFetchParams,
    JobSource,
    JobSourceError,
    JobSourceSelectionError,
    NormalizedJob,
)


def parse_nva_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    normalized = value.strip().replace(" ", "T")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def strip_html(value: str | None) -> str | None:
    if not value:
        return None

    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def parse_salary_range(value: str | None) -> tuple[int | None, int | None]:
    if not value:
        return None, None

    compact = value.replace(" ", "").replace("\xa0", "")
    matches = re.findall(r"\d+(?:[.,]\d+)?", compact)
    if not matches:
        return None, None

    values = [int(float(match.replace(",", "."))) for match in matches]
    if len(values) == 1:
        return values[0], values[0]

    return min(values), max(values)


class NvaLatviaJobSource(JobSource):
    source_name = "nva"
    base_url = "https://cvvp.nva.gov.lv"

    def fetch_jobs(self, params: JobFetchParams) -> list[NormalizedJob]:
        if params.country.lower() != "lv":
            raise JobSourceSelectionError("The NVA source is Latvia only. Use country 'lv'.")

        listings = self._fetch_listings(params)

        jobs: list[NormalizedJob] = []
        for listing in listings:
            job_id = listing.get("id")
            if job_id is None:
                continue

            detail = self._request_json(f"/data/pub_vakance/{job_id}")
            if not isinstance(detail, dict):
                raise JobSourceError(f"NVA vacancy detail for '{job_id}' was not a valid object.")

            salary_min, salary_max = parse_salary_range(detail.get("alga_no_lidz") or listing.get("alga_no_lidz"))
            remote_type = None
            if detail.get("ir_attalinati_veicams_darbs"):
                remote_type = "remote"
            elif detail.get("ir_daleji_attalinati_veicams_darbs"):
                remote_type = "hybrid"

            jobs.append(
                NormalizedJob(
                    source=self.source_name,
                    external_id=str(job_id),
                    title=detail.get("profesija") or listing.get("kla_profesija_nosaukums") or "Untitled role",
                    company=detail.get("uznemums") or listing.get("uzn_uznemums_nosaukums"),
                    location=detail.get("adrese") or listing.get("vieta"),
                    remote_type=remote_type,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    description=strip_html(detail.get("darba_apraksts")),
                    url=f"{self.base_url}/#/pub/vakances/{job_id}",
                    posted_at=parse_nva_datetime(detail.get("publicesanas_datums"))
                    or parse_nva_datetime(listing.get("publicesanas_laiks")),
                )
            )

        return jobs

    def _fetch_listings(self, params: JobFetchParams) -> list[dict]:
        base_query = {
            "limit": params.results_per_page,
            "offset": (params.page - 1) * params.results_per_page,
        }
        if self._is_remote_query(params.location):
            base_query["ir_attalinati_veicams_darbs"] = "true"

        candidates = self._build_search_candidates(params.keyword, params.location)
        if not candidates:
            candidates = [""]

        for candidate in candidates:
            list_query = dict(base_query)
            if candidate:
                list_query["nosaukums"] = candidate

            listings = self._request_json(f"/data/pub_vakance_list?{urlencode(list_query)}")
            if not isinstance(listings, list):
                raise JobSourceError("NVA list response was not a valid jobs array.")
            if listings:
                return listings

        return []

    def _build_search_text(self, keyword: str, location: str) -> str:
        parts = self._unique_parts(keyword.strip(), location.strip())
        if parts and self._is_remote_query(parts[-1]):
            parts = parts[:-1]

        return " ".join(parts).strip()

    def _build_search_candidates(self, keyword: str, location: str) -> list[str]:
        keyword_value = keyword.strip()
        location_value = location.strip()
        candidates: list[str] = []

        combined = self._build_search_text(keyword_value, location_value)
        if combined:
            candidates.append(combined)

        for candidate in self._unique_parts(keyword_value, location_value):
            if candidate and not self._is_remote_query(candidate) and candidate not in candidates:
                candidates.append(candidate)

        return candidates

    def _unique_parts(self, *values: str) -> list[str]:
        parts: list[str] = []
        seen: set[str] = set()
        for value in values:
            if not value:
                continue
            normalized = value.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            parts.append(value)

        return parts

    def _is_remote_query(self, value: str) -> bool:
        normalized = value.strip().lower()
        return normalized in {"remote", "remote only", "attalinati", "attalināts", "attalinati veicams darbs"}

    def _request_json(self, path: str) -> object:
        request = Request(
            f"{self.base_url}{path}",
            headers={
                "Accept": "application/json",
                "User-Agent": "CareerGraph/0.1",
            },
        )

        try:
            with urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise JobSourceError(f"NVA request failed with status {error.code}.") from error
        except URLError as error:
            raise JobSourceError("NVA request could not reach the public portal.") from error
