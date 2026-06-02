from app.services.job_sources.base import (
    JobFetchParams,
    JobSource,
    JobSourceNotImplementedError,
    JobSourceSelectionError,
    NormalizedJob,
)


class EuresLatviaJobSource(JobSource):
    source_name = "eures"

    def fetch_jobs(self, params: JobFetchParams) -> list[NormalizedJob]:
        if params.country.lower() != "lv":
            raise JobSourceSelectionError("The current EURES stub is intended for Latvia only. Use country 'lv'.")

        raise JobSourceNotImplementedError(
            "EURES Latvia source is stubbed only. Add the real EURES integration next."
        )
