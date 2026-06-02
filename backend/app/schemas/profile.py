from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    summary: str | None = None
    preferred_roles: str | None = None
    preferred_locations: str | None = None
    preferred_remote_type: str | None = None
    preferred_technologies: str | None = None
    salary_expectation_min: int | None = None
    salary_expectation_max: int | None = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
