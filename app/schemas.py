from datetime import date, datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# ============================================================
# ATTENDANCE STATUS
# ============================================================

class AttendanceStatus(str, Enum):

    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    LEAVE = "Leave"


# ============================================================
# STUDENT SCHEMAS
# ============================================================

class StudentCreate(BaseModel):

    student_code: str = Field(
        min_length=1,
        max_length=50
    )

    name: str = Field(
        min_length=1,
        max_length=100
    )

    # Class ID from school_classes table
    class_id: int = Field(
        gt=0
    )

    # Section ID from sections table
    section_id: int = Field(
        gt=0
    )

    roll_number: int = Field(
        gt=0
    )


class StudentUpdate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100
    )

    # Class ID from school_classes table
    class_id: int = Field(
        gt=0
    )

    # Section ID from sections table
    section_id: int = Field(
        gt=0
    )

    roll_number: int = Field(
        gt=0
    )


class StudentResponse(BaseModel):

    id: int
    student_code: str
    name: str

    class_id: int
    section_id: int

    roll_number: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class StudentListResponse(BaseModel):

    page: int
    page_size: int
    total: int
    students: list[StudentResponse]


# ============================================================
# CLASS SCHEMAS
# ============================================================

class SchoolClassCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=50
    )


class SchoolClassUpdate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=50
    )


class SchoolClassResponse(BaseModel):

    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# SECTION SCHEMAS
# ============================================================

class SectionCreate(BaseModel):

    class_id: int = Field(
        gt=0
    )

    name: str = Field(
        min_length=1,
        max_length=20
    )


class SectionUpdate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=20
    )


class SectionResponse(BaseModel):

    id: int
    class_id: int
    name: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# ATTENDANCE SCHEMAS
# ============================================================

class AttendanceCreate(BaseModel):

    student_id: int = Field(
        gt=0
    )

    attendance_date: date

    status: AttendanceStatus

    remarks: str | None = Field(
        default=None,
        max_length=255
    )

    @field_validator("attendance_date")
    @classmethod
    def validate_attendance_date(
        cls,
        value: date
    ):

        today = date.today()

        if value > today:

            raise ValueError(
                "Attendance date cannot be in the future"
            )

        return value


class AttendanceUpdate(BaseModel):

    attendance_date: date

    status: AttendanceStatus

    remarks: str | None = Field(
        default=None,
        max_length=255
    )

    @field_validator("attendance_date")
    @classmethod
    def validate_attendance_date(
        cls,
        value: date
    ):

        today = date.today()

        if value > today:

            raise ValueError(
                "Attendance date cannot be in the future"
            )

        return value


class AttendanceResponse(BaseModel):

    id: int
    student_id: int
    attendance_date: date
    status: AttendanceStatus
    remarks: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )