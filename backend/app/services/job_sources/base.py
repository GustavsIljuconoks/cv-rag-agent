from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class JobFetchParams:
    keyword: str
    location: str
    country: str
    page: int = 1
    results_per_page: int = 20


@dataclass
class NormalizedJob:
    source: str
    external_id: str
    title: str
    company: str | None
    location: str | None
    remote_type: str | None
    salary_min: int | None
    salary_max: int | None
    description: str | None
    url: str | None
    posted_at: datetime | None


class JobSourceError(RuntimeError):
    pass


class JobSourceConfigurationError(JobSourceError):
    pass


class JobSourceSelectionError(JobSourceError):
    pass


class JobSourceNotImplementedError(JobSourceError):
    pass


class JobSource(ABC):
    source_name: str

    @abstractmethod
    def fetch_jobs(self, params: JobFetchParams) -> list[NormalizedJob]:
        raise NotImplementedError
