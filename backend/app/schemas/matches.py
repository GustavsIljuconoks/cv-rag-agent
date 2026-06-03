from datetime import datetime

from pydantic import BaseModel

from app.schemas.jobs import JobRead


class MatchRead(BaseModel):
    id: int
    job_id: int
    candidate_profile_id: int
    match_score: int | None
    semantic_score: int | None
    skill_score: int | None
    seniority_score: int | None
    location_score: int | None
    salary_score: int | None
    interest_score: int | None
    explanation: str | None
    recommendation: str | None
    created_at: datetime
    matched_skills: list[str]
    missing_skills: list[str]
    job: JobRead


class MatchesResponse(BaseModel):
    has_snapshot: bool
    is_stale: bool
    evaluated_count: int
    last_run_at: datetime | None
    profile_updated_at: datetime | None
    snapshot_profile_updated_at: datetime | None
    scoring_version: str | None
    matches: list[MatchRead]
