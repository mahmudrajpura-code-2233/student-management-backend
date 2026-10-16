from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Student, SchoolClass, Section
from ..schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/students",
    tags=["Students"],
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def validate_class_and_section(
    class_id: int,
    section_id: int,
    db: Session,
):
    """
    Class aur section valid hain ya nahi check karta hai.

    Rules:
    - Class exist karni chahiye.
    - Class active honi chahiye.
    - Section exist karna chahiye.
    - Section active hona chahiye.
    - Section same class ke andar hona chahiye.
    """

    # --------------------------------------------------------
    # CHECK CLASS
    # --------------------------------------------------------

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
            detail="Class not found",
        )

    if not school_class.is_active:
        raise HTTPException(
            status_code=400,
            detail="Class is inactive",
        )

    # --------------------------------------------------------
    # CHECK SECTION
    # --------------------------------------------------------

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
            detail="Section not found",
        )

    if not section.is_active:
        raise HTTPException(
            status_code=400,
            detail="Section is inactive",
        )

    # --------------------------------------------------------
    # CHECK SECTION BELONGS TO CLASS
    # --------------------------------------------------------

    if section.class_id != class_id:
        raise HTTPException(
            status_code=400,
            detail="Section does not belong to the selected class",
        )


# ============================================================
# 1. CREATE STUDENT
# ============================================================

@router.post(
    "/",
    response_model=StudentResponse,
    status_code=201,
)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
):
    """
    New student create karta hai.

    Rules:
    - Student code unique hona chahiye.
    - Class valid aur active honi chahiye.
    - Section valid aur active hona chahiye.
    - Section selected class ka hona chahiye.
    - Roll number positive hona chahiye.
    """

    # --------------------------------------------------------
    # NORMALIZE TEXT
    # --------------------------------------------------------

    student_code = student_data.student_code.strip()
    student_name = student_data.name.strip()

    if not student_code:
        raise HTTPException(
            status_code=400,
            detail="Student code cannot be empty",
        )

    if not student_name:
        raise HTTPException(
            status_code=400,
            detail="Student name cannot be empty",
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE STUDENT CODE
    # --------------------------------------------------------

    existing_student = (
        db.query(Student)
        .filter(
            Student.student_code == student_code
        )
        .first()
    )

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Student code already exists",
        )

    # --------------------------------------------------------
    # CHECK CLASS + SECTION
    # --------------------------------------------------------

    validate_class_and_section(
        class_id=student_data.class_id,
        section_id=student_data.section_id,
        db=db,
    )

    # --------------------------------------------------------
    # CREATE STUDENT
    # --------------------------------------------------------

    new_student = Student(
        student_code=student_code,
        name=student_name,
        class_id=student_data.class_id,
        section_id=student_data.section_id,
        roll_number=student_data.roll_number,
        is_active=True,
        gr_no=student_data.gr_no,
        father_name=student_data.father_name,
        mother_name=student_data.mother_name,
        dob=student_data.dob,
        primary_phone=student_data.primary_phone,
        secondary_phone=student_data.secondary_phone,
        aadhaar_number=student_data.aadhaar_number,
        photo_url=student_data.photo_url,
        address=student_data.address,
        total_yearly_fees=student_data.total_yearly_fees,
    )

    db.add(new_student)

    try:
        db.commit()
        db.refresh(new_student)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Student could not be created",
        )

    return new_student


# ============================================================
# 2. GET STUDENTS
#
# Features:
# - Pagination
# - Search
# - Class filter
# - Section filter
# - Active/inactive filter
# ============================================================

@router.get(
    "/",
    response_model=StudentListResponse,
)
def get_students(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
    ),
    class_id: int | None = Query(
        default=None,
        gt=0,
    ),
    section_id: int | None = Query(
        default=None,
        gt=0,
    ),
    is_active: bool = Query(
        default=True,
    ),
    db: Session = Depends(get_db),
):
    """
    Students ki paginated list return karta hai.

    Default:
    - Sirf active students
    - Page 1
    - 20 records per page

    Example:

    /students/?page=1&page_size=20

    Search:

    /students/?search=Rahul

    Class:

    /students/?class_id=1

    Section:

    /students/?section_id=2

    Inactive:

    /students/?is_active=false
    """

    # --------------------------------------------------------
    # BASE QUERY
    # --------------------------------------------------------

    query = db.query(Student)

    # --------------------------------------------------------
    # ACTIVE / INACTIVE FILTER
    # --------------------------------------------------------

    query = query.filter(
        Student.is_active == is_active
    )

    # --------------------------------------------------------
    # SEARCH
    #
    # Student code OR student name
    # --------------------------------------------------------

    if search is not None:

        search_value = search.strip()

        if search_value:

            search_pattern = f"%{search_value}%"

            query = query.filter(
                (
                    Student.name.ilike(search_pattern)
                )
                |
                (
                    Student.student_code.ilike(
                        search_pattern
                    )
                )
            )

    # --------------------------------------------------------
    # CLASS FILTER
    # --------------------------------------------------------

    if class_id is not None:
        query = query.filter(
            Student.class_id == class_id
        )

    # --------------------------------------------------------
    # SECTION FILTER
    # --------------------------------------------------------

    if section_id is not None:
        query = query.filter(
            Student.section_id == section_id
        )

    # --------------------------------------------------------
    # TOTAL COUNT
    # --------------------------------------------------------

    total = query.count()

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    offset = (page - 1) * page_size

    students = (
        query
        .order_by(
            Student.roll_number.asc(),
            Student.id.asc(),
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return StudentListResponse(
        page=page,
        page_size=page_size,
        total=total,
        students=students,
    )


# ============================================================
# 3. GET SINGLE STUDENT
# ============================================================

@router.get(
    "/{student_id}",
    response_model=StudentResponse,
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """
    Student ID se single student return karta hai.

    Active aur inactive dono student
    ID ke through mil sakte hain.
    """

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
            detail="Student not found",
        )

    return student


# ============================================================
# 4. UPDATE STUDENT
# ============================================================

@router.put(
    "/{student_id}",
    response_model=StudentResponse,
)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
):
    """
    Existing student update karta hai.

    Update fields:
    - name
    - class_id
    - section_id
    - roll_number

    Student code change nahi kiya ja sakta.
    """

    # --------------------------------------------------------
    # FIND STUDENT
    # --------------------------------------------------------

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
            detail="Student not found",
        )

    # --------------------------------------------------------
    # NORMALIZE NAME
    # --------------------------------------------------------

    student_name = student_data.name.strip()

    if not student_name:
        raise HTTPException(
            status_code=400,
            detail="Student name cannot be empty",
        )

    # --------------------------------------------------------
    # CHECK CLASS + SECTION
    # --------------------------------------------------------

    validate_class_and_section(
        class_id=student_data.class_id,
        section_id=student_data.section_id,
        db=db,
    )

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    student.name = student_name
    student.class_id = student_data.class_id
    student.section_id = student_data.section_id
    student.roll_number = student_data.roll_number
    student.is_active = student_data.is_active

    if student_data.gr_no is not None:
        student.gr_no = student_data.gr_no
    if student_data.father_name is not None:
        student.father_name = student_data.father_name
    if student_data.mother_name is not None:
        student.mother_name = student_data.mother_name
    if student_data.dob is not None:
        student.dob = student_data.dob
    if student_data.primary_phone is not None:
        student.primary_phone = student_data.primary_phone
    if student_data.secondary_phone is not None:
        student.secondary_phone = student_data.secondary_phone
    if student_data.aadhaar_number is not None:
        student.aadhaar_number = student_data.aadhaar_number
    if student_data.photo_url is not None:
        student.photo_url = student_data.photo_url
    if student_data.address is not None:
        student.address = student_data.address
    if student_data.total_yearly_fees is not None:
        student.total_yearly_fees = student_data.total_yearly_fees

    try:
        db.commit()
        db.refresh(student)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Student could not be updated",
        )

    return student


# ============================================================
# 5. DEACTIVATE STUDENT
# ============================================================

@router.patch(
    "/{student_id}/deactivate",
)
def deactivate_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """
    Student ko permanently delete nahi karta.

    Sirf is_active = False karta hai.

    Isse student ka old data,
    including attendance history,
    safe rehta hai.
    """

    # --------------------------------------------------------
    # FIND STUDENT
    # --------------------------------------------------------

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
            detail="Student not found",
        )

    # --------------------------------------------------------
    # ALREADY INACTIVE
    # --------------------------------------------------------

    if not student.is_active:
        raise HTTPException(
            status_code=400,
            detail="Student is already inactive",
        )

    # --------------------------------------------------------
    # DEACTIVATE
    # --------------------------------------------------------

    student.is_active = False

    db.commit()

    return {
        "message": "Student deactivated successfully",
        "student_id": student_id,
        "is_active": False,
    }


# ============================================================
# 6. ACTIVATE STUDENT
# ============================================================

@router.patch(
    "/{student_id}/activate",
)
def activate_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """
    Previously deactivated student ko
    dobara active karta hai.
    """

    # --------------------------------------------------------
    # FIND STUDENT
    # --------------------------------------------------------

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
            detail="Student not found",
        )

    # --------------------------------------------------------
    # ALREADY ACTIVE
    # --------------------------------------------------------

    if student.is_active:
        raise HTTPException(
            status_code=400,
            detail="Student is already active",
        )

    # --------------------------------------------------------
    # CHECK CURRENT CLASS + SECTION
    #
    # Agar class/section deactivate ho chuka hai,
    # student ko activate nahi karenge.
    # --------------------------------------------------------

    validate_class_and_section(
        class_id=student.class_id,
        section_id=student.section_id,
        db=db,
    )

    student.is_active = True

    db.commit()

    return {
        "message": "Student activated successfully",
        "student_id": student_id,
        "is_active": True,
    }


# ============================================================
# 7. DELETE STUDENT
# ============================================================

@router.delete(
    "/{student_id}",
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """
    Student ko permanently delete karta hai.
    """

    # --------------------------------------------------------
    # FIND STUDENT
    # --------------------------------------------------------

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
            detail="Student not found",
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully",
        "student_id": student_id
    }