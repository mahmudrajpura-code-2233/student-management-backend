from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    SchoolClass,
    Section,
    Student,
)
from ..schemas import (
    StudentCreate,
    StudentListResponse,
    StudentResponse,
    StudentUpdate,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# ============================================================
# CREATE STUDENT
# ============================================================

@router.post("/", response_model=StudentResponse)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check duplicate student code
    # --------------------------------------------------------

    existing_student = (
        db.query(Student)
        .filter(
            Student.student_code == student.student_code
        )
        .first()
    )

    if existing_student:

        raise HTTPException(
            status_code=400,
            detail="Student code already exists"
        )

    # --------------------------------------------------------
    # Check class
    # --------------------------------------------------------

    school_class = (
        db.query(SchoolClass)
        .filter(
            SchoolClass.id == student.class_id
        )
        .first()
    )

    if not school_class:

        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    if not school_class.is_active:

        raise HTTPException(
            status_code=400,
            detail="Cannot create student in an inactive class"
        )

    # --------------------------------------------------------
    # Check section
    # --------------------------------------------------------

    section = (
        db.query(Section)
        .filter(
            Section.id == student.section_id
        )
        .first()
    )

    if not section:

        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    if not section.is_active:

        raise HTTPException(
            status_code=400,
            detail="Cannot create student in an inactive section"
        )

    # --------------------------------------------------------
    # Make sure section belongs to selected class
    # --------------------------------------------------------

    if section.class_id != student.class_id:

        raise HTTPException(
            status_code=400,
            detail="Section does not belong to the selected class"
        )

    # --------------------------------------------------------
    # Create student
    # --------------------------------------------------------

    new_student = Student(
        student_code=student.student_code,
        name=student.name,
        class_id=student.class_id,
        section_id=student.section_id,
        roll_number=student.roll_number,
    )

    db.add(new_student)

    db.commit()

    db.refresh(new_student)

    return new_student


# ============================================================
# GET STUDENTS
# ============================================================

@router.get(
    "/",
    response_model=StudentListResponse
)
def get_students(
    search: str | None = None,
    class_id: int | None = None,
    section_id: int | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Validate pagination
    # --------------------------------------------------------

    if page < 1:

        raise HTTPException(
            status_code=400,
            detail="page must be greater than 0"
        )

    if page_size < 1 or page_size > 100:

        raise HTTPException(
            status_code=400,
            detail="page_size must be between 1 and 100"
        )

    # --------------------------------------------------------
    # Allowed sorting fields
    # --------------------------------------------------------

    allowed_sort_fields = {

        "id": Student.id,

        "name": Student.name,

        "student_code": Student.student_code,

        "class_id": Student.class_id,

        "section_id": Student.section_id,

        "roll_number": Student.roll_number,
    }

    if sort_by not in allowed_sort_fields:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort_by. Allowed values: "
                "id, name, student_code, class_id, "
                "section_id, roll_number"
            )
        )

    if sort_order not in ["asc", "desc"]:

        raise HTTPException(
            status_code=400,
            detail="sort_order must be 'asc' or 'desc'"
        )

    # --------------------------------------------------------
    # Base query
    # --------------------------------------------------------

    query = (
        db.query(Student)
        .filter(
            Student.is_active == True
        )
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search:

        query = query.filter(
            (Student.name.ilike(f"%{search}%"))
            |
            (Student.student_code.ilike(f"%{search}%"))
        )

    # --------------------------------------------------------
    # Class filter
    # --------------------------------------------------------

    if class_id is not None:

        query = query.filter(
            Student.class_id == class_id
        )

    # --------------------------------------------------------
    # Section filter
    # --------------------------------------------------------

    if section_id is not None:

        query = query.filter(
            Student.section_id == section_id
        )

    # --------------------------------------------------------
    # Total count
    # --------------------------------------------------------

    total = query.count()

    # --------------------------------------------------------
    # Sorting
    # --------------------------------------------------------

    sort_column = allowed_sort_fields[sort_by]

    if sort_order == "asc":

        query = query.order_by(
            asc(sort_column)
        )

    else:

        query = query.order_by(
            desc(sort_column)
        )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    offset = (page - 1) * page_size

    students = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "students": students,
    }


# ============================================================
# GET SINGLE STUDENT
# ============================================================

@router.get(
    "/{student_id}",
    response_model=StudentResponse
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(
            Student.id == student_id
        )
        .first()
    )

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


# ============================================================
# UPDATE STUDENT
# ============================================================

@router.put(
    "/{student_id}",
    response_model=StudentResponse
)
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db)
):

    existing_student = (
        db.query(Student)
        .filter(
            Student.id == student_id
        )
        .first()
    )

    if not existing_student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # --------------------------------------------------------
    # Check class
    # --------------------------------------------------------

    school_class = (
        db.query(SchoolClass)
        .filter(
            SchoolClass.id == student.class_id
        )
        .first()
    )

    if not school_class:

        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    if not school_class.is_active:

        raise HTTPException(
            status_code=400,
            detail="Cannot assign student to an inactive class"
        )

    # --------------------------------------------------------
    # Check section
    # --------------------------------------------------------

    section = (
        db.query(Section)
        .filter(
            Section.id == student.section_id
        )
        .first()
    )

    if not section:

        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    if not section.is_active:

        raise HTTPException(
            status_code=400,
            detail="Cannot assign student to an inactive section"
        )

    # --------------------------------------------------------
    # Check class-section relationship
    # --------------------------------------------------------

    if section.class_id != student.class_id:

        raise HTTPException(
            status_code=400,
            detail="Section does not belong to the selected class"
        )

    # --------------------------------------------------------
    # Update fields
    # --------------------------------------------------------

    existing_student.name = student.name

    existing_student.class_id = student.class_id

    existing_student.section_id = student.section_id

    existing_student.roll_number = student.roll_number

    db.commit()

    db.refresh(existing_student)

    return existing_student


# ============================================================
# DEACTIVATE STUDENT
# ============================================================

@router.patch(
    "/{student_id}/deactivate",
    response_model=StudentResponse
)
def deactivate_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    existing_student = (
        db.query(Student)
        .filter(
            Student.id == student_id
        )
        .first()
    )

    if not existing_student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    existing_student.is_active = False

    db.commit()

    db.refresh(existing_student)

    return existing_student


# ============================================================
# REACTIVATE STUDENT
# ============================================================

@router.patch(
    "/{student_id}/reactivate",
    response_model=StudentResponse
)
def reactivate_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    existing_student = (
        db.query(Student)
        .filter(
            Student.id == student_id
        )
        .first()
    )

    if not existing_student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    existing_student.is_active = True

    db.commit()

    db.refresh(existing_student)

    return existing_student