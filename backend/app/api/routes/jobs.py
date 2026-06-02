from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job
from app.db.session import get_db
from app.schemas.jobs import JobRead, JobsFetchRequest, JobsFetchResponse
from app.services.job_sources import (
    JobFetchParams,
    JobSourceConfigurationError,
    JobSourceError,
    JobSourceNotImplementedError,
    JobSourceSelectionError,
    get_job_source,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/fetch", response_model=JobsFetchResponse, status_code=status.HTTP_201_CREATED)
def fetch_jobs(payload: JobsFetchRequest, db: Session = Depends(get_db)) -> JobsFetchResponse:
    try:
        source = get_job_source(payload.source)
        normalized_jobs = source.fetch_jobs(
            JobFetchParams(
                keyword=payload.keyword,
                location=payload.location,
                country=payload.country.lower(),
                page=payload.page,
                results_per_page=payload.results_per_page,
            )
        )
    except JobSourceConfigurationError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except JobSourceNotImplementedError as error:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(error)) from error
    except JobSourceSelectionError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except JobSourceError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error

    inserted_count = 0
    updated_count = 0
    persisted_jobs: list[Job] = []

    for normalized_job in normalized_jobs:
        normalized = normalized_job.__dict__
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
        source=payload.source,
        fetched_count=len(normalized_jobs),
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
