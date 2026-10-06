from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SchoolClass, Section
from ..schemas import (
    SectionCreate,
    SectionResponse,
    SectionUpdate,
)


router = APIRouter(
    prefix="/sections",
    tags=["Sections"]
)


# ============================================================
# CREATE SECTION
# ============================================================

@router.post(
    "/",
    response_model=SectionResponse
)
def create_section(
    section: SectionCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check whether class exists
    # --------------------------------------------------------

    school_class = (
        db.query(SchoolClass)
        .filter(
            SchoolClass.id == section.class_id
        )
        .first()
    )

    if not school_class:

        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    # --------------------------------------------------------
    # Do not allow section under inactive class
    # --------------------------------------------------------

    if not school_class.is_active:

        raise HTTPException(
            status_code=400,
            detail="Cannot create section for an inactive class"
        )

    # --------------------------------------------------------
    # Check duplicate section
    # --------------------------------------------------------

    existing_section = (
        db.query(Section)
        .filter(
            Section.class_id == section.class_id,
            Section.name == section.name
        )
        .first()
    )

    if existing_section:

        raise HTTPException(
            status_code=400,
            detail="Section already exists for this class"
        )

    # --------------------------------------------------------
    # Create section
    # --------------------------------------------------------

    new_section = Section(
        class_id=section.class_id,
        name=section.name
    )

    db.add(new_section)
    db.commit()
    db.refresh(new_section)

    return new_section


# ============================================================
# GET ALL SECTIONS
# ============================================================

@router.get(
    "/",
    response_model=list[SectionResponse]
)
def get_sections(
    class_id: int | None = None,
    include_inactive: bool = False,
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Validate sort order
    # --------------------------------------------------------

    if sort_order not in ["asc", "desc"]:

        raise HTTPException(
            status_code=400,
            detail="sort_order must be 'asc' or 'desc'"
        )

    # --------------------------------------------------------
    # Base query
    # --------------------------------------------------------

    query = db.query(Section)

    # --------------------------------------------------------
    # Optional class filter
    # --------------------------------------------------------

    if class_id is not None:

        # Check class exists
        school_class = (
            db.query(SchoolClass)
            .filter(
                SchoolClass.id == class_id
            )
            .first()
        )

        if not school_class:

            raise HTTPException(
                status_code=404,
                detail="Class not found"
            )

        query = query.filter(
            Section.class_id == class_id
        )

    # --------------------------------------------------------
    # Active filter
    # --------------------------------------------------------

    if not include_inactive:

        query = query.filter(
            Section.is_active == True
        )

    # --------------------------------------------------------
    # Sorting
    # --------------------------------------------------------

    if sort_order == "asc":

        query = query.order_by(
            asc(Section.name)
        )

    else:

        query = query.order_by(
            desc(Section.name)
        )

    return query.all()


# ============================================================
# GET SINGLE SECTION
# ============================================================

@router.get(
    "/{section_id}",
    response_model=SectionResponse
)
def get_section(
    section_id: int,
    db: Session = Depends(get_db)
):

    section = (
        db.query(Section)
        .filter(
            Section.id == section_id
        )
        .first()
    )

    if not section:

        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    return section


# ============================================================
# UPDATE SECTION
# ============================================================

@router.put(
    "/{section_id}",
    response_model=SectionResponse
)
def update_section(
    section_id: int,
    section: SectionUpdate,
    db: Session = Depends(get_db)
):

    existing_section = (
        db.query(Section)
        .filter(
            Section.id == section_id
        )
        .first()
    )

    if not existing_section:

        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    # --------------------------------------------------------
    # Check duplicate section name inside same class
    # --------------------------------------------------------

    duplicate_section = (
        db.query(Section)
        .filter(
            Section.class_id == existing_section.class_id,
            Section.name == section.name,
            Section.id != section_id
        )
        .first()
    )

    if duplicate_section:

        raise HTTPException(
            status_code=400,
            detail="Section already exists for this class"
        )

    existing_section.name = section.name

    db.commit()
    db.refresh(existing_section)

    return existing_section


# ============================================================
# DEACTIVATE SECTION
# ============================================================

@router.patch(
    "/{section_id}/deactivate",
    response_model=SectionResponse
)
def deactivate_section(
    section_id: int,
    db: Session = Depends(get_db)
):

    existing_section = (
        db.query(Section)
        .filter(
            Section.id == section_id
        )
        .first()
    )

    if not existing_section:

        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    existing_section.is_active = False

    db.commit()
    db.refresh(existing_section)

    return existing_section


# ============================================================
# REACTIVATE SECTION
# ============================================================

@router.patch(
    "/{section_id}/reactivate",
    response_model=SectionResponse
)
def reactivate_section(
    section_id: int,
    db: Session = Depends(get_db)
):

    existing_section = (
        db.query(Section)
        .filter(
            Section.id == section_id
        )
        .first()
    )

    if not existing_section:

        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    existing_section.is_active = True

    db.commit()
    db.refresh(existing_section)

    return existing_section