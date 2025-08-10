from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.db.models import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.db.models import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
import re


def generate_slug(name: str) -> str:
    """Generuje slug na podstawie nazwy organizacji"""
    # Usuwa polskie znaki i konwertuje na małe litery
    slug = name.lower()
    slug = re.sub(r'[ąćęłńóśźż]', lambda m: {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z'
    }[m.group()], slug)
    # Usuwa znaki specjalne i zastępuje spacjami myślnikami
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug


def create_organization(db: Session, organization: OrganizationCreate, owner_id: int) -> Organization:
    """Tworzy nową organizację"""
    # Generuje slug
    slug = generate_slug(organization.name)
    
    # Sprawdza czy slug jest unikalny
    counter = 1
    original_slug = slug
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{original_slug}-{counter}"
        counter += 1
    
    organization_data = organization.dict()
    organization_data['slug'] = slug
    organization_data['owner_id'] = owner_id
    
    db_organization = Organization(**organization_data)
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def get_organization(db: Session, organization_id: int) -> Optional[Organization]:
    """Pobiera organizację po ID"""
    return db.query(Organization).filter(Organization.id == organization_id).first()


def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[Organization]:
    """Pobiera listę organizacji z paginacją"""
    return (
        db.query(Organization)
        .order_by(desc(Organization.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_organization(
    db: Session, organization_id: int, organization_update: OrganizationUpdate
) -> Optional[Organization]:
    """Aktualizuje organizację"""
    db_organization = get_organization(db, organization_id)
    if not db_organization:
        return None
    
    update_data = organization_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_organization, field, value)
    
    db.commit()
    db.refresh(db_organization)
    return db_organization


def delete_organization(db: Session, organization_id: int) -> bool:
    """Usuwa organizację"""
    db_organization = get_organization(db, organization_id)
    if not db_organization:
        return False
    
    db.delete(db_organization)
    db.commit()
    return True


def search_organizations(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Organization]:
    """Wyszukuje organizacje po nazwie"""
    return (
        db.query(Organization)
        .filter(Organization.name.ilike(f"%{query}%"))
        .order_by(desc(Organization.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
