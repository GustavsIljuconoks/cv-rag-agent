from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job
from app.db.session import get_db
from app.schemas.jobs import JobRead, JobsFetchRequest, JobsFetchResponse
from app.services.adzuna_client import AdzunaClient, AdzunaSearchParams, parse_adzuna_datetime

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _normalize_job(raw_job: dict) -> dict:
    company = raw_job.get("company") or {}
    location = raw_job.get("location") or {}

    return {
        "source": "adzuna",
        "external_id": str(raw_job["id"]),
        "title": raw_job.get("title") or "Untitled role",
        "company": company.get("display_name"),
        "location": location.get("display_name"),
        "remote_type": None,
        "salary_min": int(raw_job["salary_min"]) if raw_job.get("salary_min") is not None else None,
        "salary_max": int(raw_job["salary_max"]) if raw_job.get("salary_max") is not None else None,
        "description": raw_job.get("description"),
        "url": raw_job.get("redirect_url"),
        "posted_at": parse_adzuna_datetime(raw_job.get("created")),
    }


@router.post("/fetch", response_model=JobsFetchResponse, status_code=status.HTTP_201_CREATED)
def fetch_jobs(payload: JobsFetchRequest, db: Session = Depends(get_db)) -> JobsFetchResponse:
    client = AdzunaClient()

    try:
        raw_jobs = client.search_jobs(
            AdzunaSearchParams(
                keyword=payload.keyword,
                location=payload.location,
                country=payload.country.lower(),
                page=payload.page,
                results_per_page=payload.results_per_page,
            )
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error

    inserted_count = 0
    updated_count = 0
    persisted_jobs: list[Job] = []

    for raw_job in raw_jobs:
        normalized = _normalize_job(raw_job)
        statement = select(Job).where(
            Job.source == normalized["source"],
            Job.external_id == normalized["external_id"],
        )
        job = db.scalar(statement)

        if job is None:
            job = Job(**normalized)
            db.add(job)
            inserted_count += 1
        else:
            for field, value in normalized.items():
                setattr(job, field, value)
            updated_count += 1

        persisted_jobs.append(job)

    db.commit()

    for job in persisted_jobs:
        db.refresh(job)

    return JobsFetchResponse(
        fetched_count=len(raw_jobs),
        inserted_count=inserted_count,
        updated_count=updated_count,
        jobs=persisted_jobs,
    )


@router.get("", response_model=list[JobRead])
def list_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Job]:
    statement = select(Job).order_by(Job.posted_at.desc().nullslast(), Job.created_at.desc()).limit(limit)
    return list(db.scalars(statement))
