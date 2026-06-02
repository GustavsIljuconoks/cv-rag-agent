from app.services.job_sources.adzuna import AdzunaJobSource
from app.services.job_sources.base import JobSource, JobSourceSelectionError
from app.services.job_sources.eures import EuresLatviaJobSource
from app.services.job_sources.nva import NvaLatviaJobSource


def get_job_source(source_name: str) -> JobSource:
    normalized = source_name.lower()

    if normalized == "adzuna":
        return AdzunaJobSource()

    if normalized == "eures":
        return EuresLatviaJobSource()

    if normalized == "nva":
        return NvaLatviaJobSource()

    raise JobSourceSelectionError(f"Unknown job source '{source_name}'.")
