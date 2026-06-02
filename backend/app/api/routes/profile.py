from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CandidateProfile
from app.db.session import get_db
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


def _get_current_profile(db: Session) -> CandidateProfile | None:
    statement = select(CandidateProfile).order_by(CandidateProfile.updated_at.desc(), CandidateProfile.id.desc()).limit(1)
    return db.scalar(statement)


def _apply_profile_payload(profile: CandidateProfile, payload: ProfileCreate | ProfileUpdate) -> CandidateProfile:
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)

    return profile


@router.post("", response_model=ProfileRead)
def create_profile(
    payload: ProfileCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> CandidateProfile:
    profile = _get_current_profile(db)

    if profile is None:
        profile = CandidateProfile(**payload.model_dump())
        db.add(profile)
        response.status_code = status.HTTP_201_CREATED
    else:
        _apply_profile_payload(profile, payload)
        response.status_code = status.HTTP_200_OK

    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=ProfileRead)
def get_profile(db: Session = Depends(get_db)) -> CandidateProfile:
    profile = _get_current_profile(db)

    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return profile


@router.put("", response_model=ProfileRead)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db)) -> CandidateProfile:
    profile = _get_current_profile(db)

    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    _apply_profile_payload(profile, payload)
    db.commit()
    db.refresh(profile)
    return profile
