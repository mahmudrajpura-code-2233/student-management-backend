# ============================================================
# ATTENDANCE ROUTES
# ============================================================
#
# Is file mein Student Attendance Management ke saare
# API endpoints hain.
#
# Features:
# 1. Create attendance
# 2. Get all attendance
# 3. Get attendance by student
# 4. Get attendance by date
# 5. Get attendance by date range
# 6. Get student attendance summary
# 7. Update attendance
# 8. Delete attendance
# ============================================================


from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Attendance, Student
from ..schemas import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


# ============================================================
# 1. CREATE ATTENDANCE
# ============================================================

@router.post(
    "/",
    response_model=AttendanceResponse
)
def create_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db)
):
    """
    Student ki attendance create karta hai.

    Rules:
    - Student exist karna chahiye.
    - Student active hona chahiye.
    - Future date allowed nahi hai.
    - Ek student ki ek date par sirf ek attendance.
    """

    # --------------------------------------------------------
    # CHECK STUDENT
    # --------------------------------------------------------

    student = (
        db.query(Student)
        .filter(
            Student.id == attendance.student_id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # --------------------------------------------------------
    # CHECK ACTIVE STUDENT
    # --------------------------------------------------------

    if not student.is_active:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot mark attendance for "
                "an inactive student"
            )
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE ATTENDANCE
    # --------------------------------------------------------

    existing_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.student_id
            == attendance.student_id,
            Attendance.attendance_date
            == attendance.attendance_date
        )
        .first()
    )

    if existing_attendance:
        raise HTTPException(
            status_code=400,
            detail="Attendance already marked for this date"
        )

    # --------------------------------------------------------
    # CREATE ATTENDANCE
    # --------------------------------------------------------

    new_attendance = Attendance(
        student_id=attendance.student_id,
        attendance_date=attendance.attendance_date,
        status=attendance.status,
        remarks=attendance.remarks,
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return new_attendance


# ============================================================
# 2. GET ALL ATTENDANCE
# ============================================================

@router.get(
    "/",
    response_model=list[AttendanceResponse]
)
def get_attendance(
    db: Session = Depends(get_db)
):
    """
    Saare attendance records return karta hai.

    Latest date pehle aayegi.
    """

    return (
        db.query(Attendance)
        .order_by(
            Attendance.attendance_date.desc()
        )
        .all()
    )


# ============================================================
# 3. GET ATTENDANCE SUMMARY
# ============================================================
#
# IMPORTANT:
# Ye route generic:
#
# /student/{student_id}
#
# se PEHLE hona chahiye.
#
# Isse:
# /attendance/student/1/summary
#
# correctly match hoga.
# ============================================================

@router.get(
    "/student/{student_id}/summary"
)
def attendance_summary(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Student ki attendance summary return karta hai.

    Example response:

    {
        "student_id": 1,
        "total_days": 10,
        "present": 8,
        "absent": 1,
        "late": 1,
        "leave": 0,
        "attendance_percentage": 80.0
    }
    """

    # --------------------------------------------------------
    # CHECK STUDENT
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
            detail="Student not found"
        )

    # --------------------------------------------------------
    # GET ATTENDANCE RECORDS
    # --------------------------------------------------------

    records = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id
        )
        .all()
    )

    # --------------------------------------------------------
    # TOTAL DAYS
    # --------------------------------------------------------

    total_days = len(records)

    # --------------------------------------------------------
    # COUNT PRESENT
    # --------------------------------------------------------

    present = sum(
        1
        for record in records
        if record.status == "Present"
    )

    # --------------------------------------------------------
    # COUNT ABSENT
    # --------------------------------------------------------

    absent = sum(
        1
        for record in records
        if record.status == "Absent"
    )

    # --------------------------------------------------------
    # COUNT LATE
    # --------------------------------------------------------

    late = sum(
        1
        for record in records
        if record.status == "Late"
    )

    # --------------------------------------------------------
    # COUNT LEAVE
    # --------------------------------------------------------

    leave = sum(
        1
        for record in records
        if record.status == "Leave"
    )

    # --------------------------------------------------------
    # ATTENDANCE PERCENTAGE
    # --------------------------------------------------------
    #
    # Current rule:
    #
    # Present / Total attendance records * 100
    #
    # School ke final attendance rules hum baad mein
    # customize kar sakte hain.
    # --------------------------------------------------------

    attendance_percentage = (
        (present / total_days) * 100
        if total_days > 0
        else 0
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "student_id": student_id,
        "total_days": total_days,
        "present": present,
        "absent": absent,
        "late": late,
        "leave": leave,
        "attendance_percentage": round(
            attendance_percentage,
            2
        ),
    }


# ============================================================
# 4. GET STUDENT ATTENDANCE
# ============================================================

@router.get(
    "/student/{student_id}",
    response_model=list[AttendanceResponse]
)
def get_student_attendance(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Ek student ki complete attendance history return karta hai.
    """

    # --------------------------------------------------------
    # CHECK STUDENT
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
            detail="Student not found"
        )

    # --------------------------------------------------------
    # GET ATTENDANCE
    # --------------------------------------------------------

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id
        )
        .order_by(
            Attendance.attendance_date.desc()
        )
        .all()
    )

    return attendance_records


# ============================================================
# 5. GET ATTENDANCE BY DATE
# ============================================================

@router.get(
    "/date/{attendance_date}",
    response_model=list[AttendanceResponse]
)
def get_attendance_by_date(
    attendance_date: date,
    db: Session = Depends(get_db)
):
    """
    Particular date ki attendance return karta hai.

    Example:

    /attendance/date/2026-10-05
    """

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.attendance_date
            == attendance_date
        )
        .all()
    )

    return attendance_records


# ============================================================
# 6. GET ATTENDANCE BY DATE RANGE
# ============================================================

@router.get(
    "/range",
    response_model=list[AttendanceResponse]
)
def get_attendance_by_range(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """
    Do dates ke beech attendance return karta hai.

    Example:

    /attendance/range
    ?start_date=2026-10-01
    &end_date=2026-10-05
    """

    # --------------------------------------------------------
    # VALIDATE DATE RANGE
    # --------------------------------------------------------

    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be greater than end_date"
        )

    # --------------------------------------------------------
    # GET RECORDS
    # --------------------------------------------------------

    attendance_records = (
        db.query(Attendance)
        .filter(
            Attendance.attendance_date
            >= start_date,
            Attendance.attendance_date
            <= end_date
        )
        .order_by(
            Attendance.attendance_date.asc()
        )
        .all()
    )

    return attendance_records


# ============================================================
# 7. UPDATE ATTENDANCE
# ============================================================

@router.put(
    "/{attendance_id}",
    response_model=AttendanceResponse
)
def update_attendance(
    attendance_id: int,
    attendance: AttendanceUpdate,
    db: Session = Depends(get_db)
):
    """
    Existing attendance update karta hai.

    Student change nahi kiya ja sakta.
    Sirf:
    - attendance_date
    - status
    - remarks
    update honge.
    """

    # --------------------------------------------------------
    # FIND ATTENDANCE
    # --------------------------------------------------------

    existing_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.id == attendance_id
        )
        .first()
    )

    if not existing_attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE DATE
    # --------------------------------------------------------
    #
    # Same student ki same date par doosri attendance
    # allowed nahi hai.
    # --------------------------------------------------------

    duplicate_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.student_id
            == existing_attendance.student_id,

            Attendance.attendance_date
            == attendance.attendance_date,

            Attendance.id != attendance_id
        )
        .first()
    )

    if duplicate_attendance:
        raise HTTPException(
            status_code=400,
            detail="Attendance already exists for this date"
        )

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    existing_attendance.attendance_date = (
        attendance.attendance_date
    )

    existing_attendance.status = (
        attendance.status
    )

    existing_attendance.remarks = (
        attendance.remarks
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    db.commit()
    db.refresh(existing_attendance)

    return existing_attendance


# ============================================================
# 8. DELETE ATTENDANCE
# ============================================================

@router.delete(
    "/{attendance_id}"
)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
):
    """
    Attendance record permanently delete karta hai.

    NOTE:
    Production version mein hum later audit/soft-delete
    approach consider kar sakte hain.
    """

    # --------------------------------------------------------
    # FIND ATTENDANCE
    # --------------------------------------------------------

    existing_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.id == attendance_id
        )
        .first()
    )

    if not existing_attendance:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    db.delete(existing_attendance)
    db.commit()

    return {
        "message": "Attendance deleted successfully",
        "attendance_id": attendance_id
    }