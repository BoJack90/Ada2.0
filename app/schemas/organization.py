from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass  # slug będzie generowany automatycznie


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    id: int
    slug: str
    is_active: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
