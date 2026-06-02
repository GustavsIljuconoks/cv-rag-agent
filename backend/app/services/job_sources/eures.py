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
            "Official EURES vacancy extraction is not available here. EURES terms prohibit screen scraping and state that only recognised EURES partner organisations may extract vacancy data via their API or similar technologies."
        )
