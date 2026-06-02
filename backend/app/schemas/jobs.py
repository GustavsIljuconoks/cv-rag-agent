from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class JobsFetchRequest(BaseModel):
    source: Literal["adzuna", "eures"] = "adzuna"
    keyword: str = Field(min_length=1)
    location: str = Field(min_length=1)
    country: str = Field(min_length=2, max_length=2)
    page: int = Field(default=1, ge=1)
    results_per_page: int = Field(default=20, ge=1, le=50)


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
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
    created_at: datetime
    updated_at: datetime


class JobsFetchResponse(BaseModel):
    source: str
    fetched_count: int
    inserted_count: int
    updated_count: int
    jobs: list[JobRead]
