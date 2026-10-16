from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SchoolClass
from ..schemas import (
    SchoolClassCreate,
    SchoolClassResponse,
    SchoolClassUpdate,
)


router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)


# ============================================================
# CREATE CLASS
# ============================================================

@router.post(
    "/",
    response_model=SchoolClassResponse
)
def create_class(
    school_class: SchoolClassCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check duplicate class name
    # --------------------------------------------------------

    existing_class = (
        db.query(SchoolClass)
        .filter(
            SchoolClass.name == school_class.name
        )
        .first()
    )

    if existing_class:

        raise HTTPException(
            status_code=400,
            detail="Class already exists"
        )

    # --------------------------------------------------------
    # Create new class
    # --------------------------------------------------------

    new_class = SchoolClass(
        name=school_class.name
    )

    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return new_class


# ============================================================
# GET ALL CLASSES
# ============================================================

@router.get(
    "/",
    response_model=list[SchoolClassResponse]
)
def get_classes(
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

    query = db.query(SchoolClass)

    # --------------------------------------------------------
    # By default only active classes
    # --------------------------------------------------------

    if not include_inactive:

        query = query.filter(
            SchoolClass.is_active == True
        )

    # --------------------------------------------------------
    # Sorting
    # --------------------------------------------------------

    if sort_order == "asc":

        query = query.order_by(
            asc(SchoolClass.name)
        )

    else:

        query = query.order_by(
            desc(SchoolClass.name)
        )

    return query.all()


# ============================================================
# GET SINGLE CLASS
# ============================================================

@router.get(
    "/{class_id}",
    response_model=SchoolClassResponse
)
def get_class(
    class_id: int,
    db: Session = Depends(get_db)
):

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

    return school_class


# ============================================================
# UPDATE CLASS
# ============================================================

@router.put(
    "/{class_id}",
    response_model=SchoolClassResponse
)
def update_class(
    class_id: int,
    school_class: SchoolClassUpdate,
    db: Session = Depends(get_db)
):

    existing_class = (
        db.query(SchoolClass)
        .filter(
            SchoolClass.id == class_id
        )
        .first()
    )

    if not existing_class:

        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    # --------------------------------------------------------
    # Check duplicate name
    # --------------------------------------------------------

    duplicate_class = (
        db.query(SchoolClass)
        .filter(
            SchoolClass.name == school_class.name,
            SchoolClass.id != class_id
        )
        .first()
    )

    if duplicate_class:

        raise HTTPException(
            status_code=400,
            detail="Class already exists"
        )

    existing_class.name = school_class.name

    db.commit()
    db.refresh(existing_class)

    return existing_class


# ============================================================
# DEACTIVATE CLASS
# ============================================================

@router.patch(
    "/{class_id}/deactivate",
    response_model=SchoolClassResponse
)
def deactivate_class(
    class_id: int,
    db: Session = Depends(get_db)
):

    existing_class = (
        db.query(SchoolClass)
        .filter(
            SchoolClass.id == class_id
        )
        .first()
    )

    if not existing_class:

        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    existing_class.is_active = False

    db.commit()
    db.refresh(existing_class)

    return existing_class


# ============================================================
# DELETE CLASS
# ============================================================

@router.delete(
    "/{class_id}"
)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db)
):

    existing_class = (
        db.query(SchoolClass)
        .filter(
            SchoolClass.id == class_id
        )
        .first()
    )

    if not existing_class:

        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    db.delete(existing_class)
    db.commit()

    return {
        "message": "Class deleted successfully",
        "class_id": class_id
    }


# ============================================================
# REACTIVATE CLASS
# ============================================================

@router.patch(
    "/{class_id}/activate",
    response_model=SchoolClassResponse
)
def activate_class(
    class_id: int,
    db: Session = Depends(get_db)
):

    existing_class = (
        db.query(SchoolClass)
        .filter(
            SchoolClass.id == class_id
        )
        .first()
    )

    if not existing_class:

        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    existing_class.is_active = True

    db.commit()
    db.refresh(existing_class)

    return existing_class