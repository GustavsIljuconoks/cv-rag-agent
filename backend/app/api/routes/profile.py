from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CandidateProfile
from app.db.session import get_db
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)) -> CandidateProfile:
    profile = CandidateProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=ProfileRead)
def get_profile(db: Session = Depends(get_db)) -> CandidateProfile:
    statement = select(CandidateProfile).order_by(CandidateProfile.id.desc()).limit(1)
    profile = db.scalar(statement)

    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return profile


@router.put("", response_model=ProfileRead)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db)) -> CandidateProfile:
    statement = select(CandidateProfile).order_by(CandidateProfile.id.desc()).limit(1)
    profile = db.scalar(statement)

    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    for field, value in payload.model_dump().items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
