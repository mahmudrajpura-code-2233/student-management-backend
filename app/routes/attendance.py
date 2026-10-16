from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Attendance, Student
from ..schemas import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceSummaryResponse,
    AttendanceDetailResponse,
    AttendanceUpdate,
    BulkAttendanceCreate,
    BulkAttendanceResponse,
)

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


# ============================================================
# 1. CREATE SINGLE ATTENDANCE
# POST /attendance/
# ============================================================

@router.post(
    "/",
    response_model=AttendanceResponse
)
def create_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == attendance_data.student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if not student.is_active:
        raise HTTPException(
            status_code=400,
            detail="Student is not active"
        )

    existing = db.query(Attendance).filter(
        Attendance.student_id == attendance_data.student_id,
        Attendance.attendance_date == attendance_data.attendance_date
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Attendance already exists for this student on this date"
        )

    attendance = Attendance(
        student_id=attendance_data.student_id,
        attendance_date=attendance_data.attendance_date,
        status=attendance_data.status.value,
        remarks=attendance_data.remarks,
    )

    db.add(attendance)

    db.commit()

    db.refresh(attendance)

    return attendance


# ============================================================
# 2. GET ATTENDANCE
# GET /attendance/
# ============================================================

@router.get(
    "/",
    response_model=list[AttendanceResponse]
)
def get_attendance(
    student_id: int | None = Query(default=None),
    attendance_date: date | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Attendance)

    if student_id is not None:
        query = query.filter(
            Attendance.student_id == student_id
        )

    if attendance_date is not None:
        query = query.filter(
            Attendance.attendance_date == attendance_date
        )

    if status is not None:
        query = query.filter(
            Attendance.status == status
        )

    return query.order_by(
        Attendance.attendance_date.desc(),
        Attendance.id.desc()
    ).all()


# ============================================================
# 3. STUDENT ATTENDANCE SUMMARY
# GET /attendance/student/{student_id}/summary
# ============================================================

@router.get(
    "/student/{student_id}/summary",
    response_model=AttendanceSummaryResponse
)
def get_student_attendance_summary(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    records = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()

    total_days = len(records)

    present_days = sum(
        1
        for record in records
        if record.status == "Present"
    )

    absent_days = sum(
        1
        for record in records
        if record.status == "Absent"
    )

    late_days = sum(
        1
        for record in records
        if record.status == "Late"
    )

    leave_days = sum(
        1
        for record in records
        if record.status == "Leave"
    )

    attendance_percentage = (
        (present_days / total_days) * 100
        if total_days > 0
        else 0
    )

    return AttendanceSummaryResponse(
        student_id=student_id,
        student_name=student.name,
        total_days=total_days,
        present_days=present_days,
        absent_days=absent_days,
        late_days=late_days,
        leave_days=leave_days,
        attendance_percentage=attendance_percentage,
    )


# ============================================================
# 4. STUDENT ATTENDANCE HISTORY
# GET /attendance/student/{student_id}
# ============================================================

@router.get(
    "/student/{student_id}",
    response_model=list[AttendanceResponse]
)
def get_student_attendance_history(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).order_by(
        Attendance.attendance_date.desc(),
        Attendance.id.desc()
    ).all()


# ============================================================
# 5. ATTENDANCE BY DATE
# GET /attendance/date/{attendance_date}
# ============================================================

@router.get(
    "/date/{attendance_date}",
    response_model=list[AttendanceDetailResponse]
)
def get_attendance_by_date(
    attendance_date: date,
    class_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Attendance, Student)
        .join(
            Student,
            Attendance.student_id == Student.id
        )
        .filter(
            Attendance.attendance_date == attendance_date
        )
    )

    if class_id is not None:
        query = query.filter(Student.class_id == class_id)

    if section_id is not None:
        query = query.filter(Student.section_id == section_id)

    results = query.order_by(Student.id).all()

    response = []

    for attendance, student in results:

        response.append(
            AttendanceDetailResponse(
                id=attendance.id,
                student_id=attendance.student_id,
                attendance_date=attendance.attendance_date,
                status=attendance.status,
                remarks=attendance.remarks,
                created_at=attendance.created_at,
                student_code=student.student_code,
                student_name=student.name,
            )
        )

    return response


# ============================================================
# 6. ATTENDANCE RANGE
# GET /attendance/range
# ============================================================

@router.get(
    "/range",
    response_model=list[AttendanceDetailResponse]
)
def get_attendance_range(
    start_date: date,
    end_date: date,
    student_id: int | None = Query(default=None),
    class_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be greater than end_date"
        )

    query = (
        db.query(Attendance, Student)
        .join(
            Student,
            Attendance.student_id == Student.id
        )
        .filter(
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date
        )
    )

    if student_id is not None:
        query = query.filter(
            Attendance.student_id == student_id
        )

    if class_id is not None:
        query = query.filter(Student.class_id == class_id)

    if section_id is not None:
        query = query.filter(Student.section_id == section_id)

    results = query.order_by(
        Attendance.attendance_date.desc(),
        Attendance.id.desc()
    ).all()

    response = []

    for attendance, student in results:

        response.append(
            AttendanceDetailResponse(
                id=attendance.id,
                student_id=attendance.student_id,
                attendance_date=attendance.attendance_date,
                status=attendance.status,
                remarks=attendance.remarks,
                created_at=attendance.created_at,
                student_code=student.student_code,
                student_name=student.name,
            )
        )

    return response


# ============================================================
# 7. BULK ATTENDANCE
# POST /attendance/bulk
# ============================================================

@router.post(
    "/bulk",
    response_model=BulkAttendanceResponse
)
def create_bulk_attendance(
    attendance_data: BulkAttendanceCreate,
    db: Session = Depends(get_db)
):
    student_ids = [
        item.student_id
        for item in attendance_data.records
    ]

    # Same student repeated in same request
    if len(student_ids) != len(set(student_ids)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate student_id found in request"
        )

    created_records = []

    for item in attendance_data.records:

        student = db.query(Student).filter(
            Student.id == item.student_id
        ).first()

        if not student:
            raise HTTPException(
                status_code=404,
                detail=f"Student {item.student_id} not found"
            )

        if not student.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Student {item.student_id} is not active"
            )

        existing = db.query(Attendance).filter(
            Attendance.student_id == item.student_id,
            Attendance.attendance_date == attendance_data.attendance_date
        ).first()

        # Already exists -> skip
        if existing:
            continue

        attendance = Attendance(
            student_id=item.student_id,
            attendance_date=attendance_data.attendance_date,
            status=item.status.value,
            remarks=item.remarks,
        )

        db.add(attendance)

        created_records.append(attendance)

    db.commit()

    for attendance in created_records:
        db.refresh(attendance)

    return BulkAttendanceResponse(
        message="Bulk attendance processed successfully",
        successful_records=len(created_records),
        failed_records=len(attendance_data.records) - len(created_records),
    )


# ============================================================
# 8. CLASS ATTENDANCE SUMMARY
# GET /attendance/class/{class_id}/summary
# ============================================================

@router.get(
    "/class/{class_id}/summary"
)
def get_class_attendance_summary(
    class_id: int,
    attendance_date: date,
    db: Session = Depends(get_db)
):
    students = db.query(Student).filter(
        Student.class_id == class_id,
        Student.is_active == True
    ).all()

    total_students = len(students)

    if total_students == 0:

        return {
            "class_id": class_id,
            "attendance_date": attendance_date,
            "total_students": 0,
            "marked_students": 0,
            "present": 0,
            "absent": 0,
            "late": 0,
            "leave": 0,
            "attendance_percentage": 0,
        }

    student_ids = [
        student.id
        for student in students
    ]

    records = db.query(Attendance).filter(
        Attendance.student_id.in_(student_ids),
        Attendance.attendance_date == attendance_date
    ).all()

    present = sum(
        1
        for record in records
        if record.status == "Present"
    )

    absent = sum(
        1
        for record in records
        if record.status == "Absent"
    )

    late = sum(
        1
        for record in records
        if record.status == "Late"
    )

    leave = sum(
        1
        for record in records
        if record.status == "Leave"
    )

    marked_students = len(records)

    attendance_percentage = (
        (present / marked_students) * 100
        if marked_students > 0
        else 0
    )

    return {
        "class_id": class_id,
        "attendance_date": attendance_date,
        "total_students": total_students,
        "marked_students": marked_students,
        "present": present,
        "absent": absent,
        "late": late,
        "leave": leave,
        "attendance_percentage": attendance_percentage,
    }


# ============================================================
# 9. UPDATE ATTENDANCE
# PUT /attendance/{attendance_id}
# ============================================================

@router.put(
    "/{attendance_id}",
    response_model=AttendanceResponse
)
def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db)
):
    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    # --------------------------------------------------------
    # New values
    # --------------------------------------------------------

    new_date = (
        attendance_data.attendance_date
        if attendance_data.attendance_date is not None
        else attendance.attendance_date
    )

    # --------------------------------------------------------
    # Duplicate check
    # --------------------------------------------------------

    if new_date != attendance.attendance_date:

        existing = db.query(Attendance).filter(
            Attendance.student_id == attendance.student_id,
            Attendance.attendance_date == new_date,
            Attendance.id != attendance_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Attendance already exists for this student on this date"
            )

    # --------------------------------------------------------
    # Update fields
    # --------------------------------------------------------

    if attendance_data.attendance_date is not None:
        attendance.attendance_date = attendance_data.attendance_date

    if attendance_data.status is not None:
        attendance.status = attendance_data.status.value

    if attendance_data.remarks is not None:
        attendance.remarks = attendance_data.remarks

    db.commit()

    db.refresh(attendance)

    return attendance


# ============================================================
# 10. DELETE ATTENDANCE
# DELETE /attendance/{attendance_id}
# ============================================================

@router.delete(
    "/{attendance_id}"
)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
):
    attendance = db.query(Attendance).filter(
        Attendance.id == attendance_id
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    db.delete(attendance)

    db.commit()

    return {
        "message": "Attendance deleted successfully",
        "attendance_id": attendance_id
    }