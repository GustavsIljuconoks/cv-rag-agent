from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import CandidateProfile, Job, JobMatch
from app.db.session import get_db
from app.schemas.jobs import JobRead
from app.schemas.matches import MatchRead, MatchesResponse
from app.services.matching import MATCH_RUN_JOB_LIMIT, derive_transient_match_details, match_jobs

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/run", response_model=MatchesResponse)
def run_matches(db: Session = Depends(get_db)) -> MatchesResponse:
    profile = _get_current_profile(db)

    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    jobs = _get_recent_jobs(db)
    match_results = match_jobs(profile, jobs)

    db.execute(delete(JobMatch).where(JobMatch.candidate_profile_id == profile.id))

    for result in match_results:
        db.add(
            JobMatch(
                job_id=result.job.id,
                candidate_profile_id=profile.id,
                match_score=result.match_score,
                semantic_score=None,
                skill_score=result.skill_score,
                seniority_score=None,
                location_score=result.location_score,
                salary_score=result.salary_score,
                interest_score=result.interest_score,
                explanation=result.explanation,
                recommendation=result.recommendation,
            )
        )

    db.commit()

    return _build_matches_response(db, profile)


@router.get("", response_model=MatchesResponse)
def get_matches(db: Session = Depends(get_db)) -> MatchesResponse:
    profile = _get_current_profile(db)

    if profile is None:
        return MatchesResponse(
            has_snapshot=False,
            is_stale=False,
            evaluated_count=0,
            last_run_at=None,
            profile_updated_at=None,
            matches=[],
        )

    return _build_matches_response(db, profile)


def _build_matches_response(db: Session, profile: CandidateProfile) -> MatchesResponse:
    last_run_at = db.scalar(
        select(func.max(JobMatch.created_at)).where(JobMatch.candidate_profile_id == profile.id)
    )
    rows = db.execute(
        select(JobMatch, Job)
        .join(Job, Job.id == JobMatch.job_id)
        .where(JobMatch.candidate_profile_id == profile.id)
        .order_by(JobMatch.match_score.desc(), Job.posted_at.desc().nullslast(), Job.created_at.desc())
    ).all()

    matches: list[MatchRead] = []
    for job_match, job in rows:
        transient = derive_transient_match_details(profile, job)
        matches.append(
            MatchRead(
                id=job_match.id,
                job_id=job_match.job_id,
                candidate_profile_id=job_match.candidate_profile_id,
                match_score=job_match.match_score,
                semantic_score=job_match.semantic_score,
                skill_score=job_match.skill_score,
                seniority_score=job_match.seniority_score,
                location_score=job_match.location_score,
                salary_score=job_match.salary_score,
                interest_score=job_match.interest_score,
                explanation=job_match.explanation,
                recommendation=job_match.recommendation,
                created_at=job_match.created_at,
                matched_skills=transient.matched_skills,
                missing_skills=transient.missing_skills,
                job=JobRead.model_validate(job),
            )
        )

    return MatchesResponse(
        has_snapshot=bool(matches),
        is_stale=bool(last_run_at and profile.updated_at > last_run_at),
        evaluated_count=len(matches),
        last_run_at=last_run_at,
        profile_updated_at=profile.updated_at,
        matches=matches,
    )


def _get_current_profile(db: Session) -> CandidateProfile | None:
    statement = select(CandidateProfile).order_by(CandidateProfile.updated_at.desc(), CandidateProfile.id.desc()).limit(1)
    return db.scalar(statement)


def _get_recent_jobs(db: Session) -> list[Job]:
    statement = (
        select(Job)
        .order_by(Job.posted_at.desc().nullslast(), Job.created_at.desc())
        .limit(MATCH_RUN_JOB_LIMIT)
    )
    return list(db.scalars(statement))
