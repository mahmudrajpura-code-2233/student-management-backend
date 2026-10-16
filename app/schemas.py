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

    student_code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    class_id: int = Field(gt=0)
    section_id: int = Field(gt=0)
    roll_number: int = Field(gt=0)

    gr_no: str | None = None
    father_name: str | None = None
    mother_name: str | None = None
    dob: date | None = None
    primary_phone: str | None = None
    secondary_phone: str | None = None
    aadhaar_number: str | None = None
    photo_url: str | None = None
    address: str | None = None
    total_yearly_fees: float | None = None


class StudentUpdate(BaseModel):

    name: str = Field(min_length=1, max_length=100)
    class_id: int = Field(gt=0)
    section_id: int = Field(gt=0)
    roll_number: int = Field(gt=0)
    is_active: bool = True

    gr_no: str | None = None
    father_name: str | None = None
    mother_name: str | None = None
    dob: date | None = None
    primary_phone: str | None = None
    secondary_phone: str | None = None
    aadhaar_number: str | None = None
    photo_url: str | None = None
    address: str | None = None
    total_yearly_fees: float | None = None


class StudentResponse(BaseModel):

    id: int
    student_code: str
    name: str

    class_id: int
    section_id: int

    roll_number: int
    is_active: bool

    gr_no: str | None = None
    father_name: str | None = None
    mother_name: str | None = None
    dob: date | None = None
    primary_phone: str | None = None
    secondary_phone: str | None = None
    aadhaar_number: str | None = None
    photo_url: str | None = None
    address: str | None = None
    total_yearly_fees: float | None = None

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

class AttendanceSummaryResponse(BaseModel):
    total_days: int = 0
    present_days: int = 0
    absent_days: int = 0
    late_days: int = 0
    leave_days: int = 0
    attendance_percentage: float = 0.0

class AttendanceDetailResponse(BaseModel):
    id: int
    student_id: int
    attendance_date: date
    status: str
    remarks: str | None = None
    created_at: datetime
    student_code: str | None = None
    student_name: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )

class BulkAttendanceRecord(BaseModel):
    student_id: int
    status: AttendanceStatus
    remarks: str | None = None

class BulkAttendanceCreate(BaseModel):
    attendance_date: date
    records: list[BulkAttendanceRecord]

class BulkAttendanceResponse(BaseModel):
    message: str
    successful_records: int
    failed_records: int

class ClassAttendanceSummaryResponse(BaseModel):
    total_students: int = 0
    marked_students: int = 0
    present: int = 0
    absent: int = 0
    late: int = 0
    leave: int = 0
    attendance_percentage: float = 0.0


# ============================================================
# USER SCHEMAS
# ============================================================

from pydantic import EmailStr

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str = Field(min_length=6)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    role: str | None = None

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

# Teacher
class TeacherBase(BaseModel):
    teacher_code: str
    name: str
    mobile: str
    email: Optional[str] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    joining_date: date
    is_active: bool = True

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    is_active: Optional[bool] = None

class TeacherResponse(TeacherBase):
    id: int
    user_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

# Subject
class SubjectBase(BaseModel):
    subject_name: str
    subject_code: str
    is_active: bool = True

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = None
    is_active: Optional[bool] = None

class SubjectResponse(SubjectBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Assignment
class AssignmentBase(BaseModel):
    teacher_id: int
    subject_id: int
    class_id: int
    section_id: Optional[int] = None
    is_active: bool = True

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    is_active: Optional[bool] = None

class AssignmentResponse(AssignmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Parent
class ParentBase(BaseModel):
    student_id: int
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    guardian_name: Optional[str] = None
    mobile: str
    email: Optional[str] = None
    address: Optional[str] = None
    relation_to_student: Optional[str] = None

class ParentCreate(ParentBase):
    pass

class ParentUpdate(BaseModel):
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    guardian_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    relation_to_student: Optional[str] = None

class ParentResponse(ParentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Exam
class ExamBase(BaseModel):
    exam_name: str
    academic_year: str
    exam_date: date
    class_id: int
    subject_id: int
    total_marks: int
    passing_marks: int

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    exam_date: Optional[date] = None
    total_marks: Optional[int] = None
    passing_marks: Optional[int] = None

class ExamResponse(ExamBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ExamResult
class ExamResultBase(BaseModel):
    exam_id: int
    student_id: int
    obtained_marks: float
    percentage: Optional[float] = None
    grade: Optional[str] = None
    status: Optional[str] = None
    rank: Optional[int] = None

class ExamResultCreate(ExamResultBase):
    pass

class ExamResultUpdate(BaseModel):
    obtained_marks: Optional[float] = None
    percentage: Optional[float] = None
    grade: Optional[str] = None
    status: Optional[str] = None
    rank: Optional[int] = None

class ExamResultResponse(ExamResultBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# FeeStructure
class FeeStructureBase(BaseModel):
    academic_year: str
    class_id: int
    fee_type: str
    amount: float

class FeeStructureCreate(FeeStructureBase):
    pass

class FeeStructureUpdate(BaseModel):
    amount: Optional[float] = None

class FeeStructureResponse(FeeStructureBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# StudentFee
class StudentFeeBase(BaseModel):
    student_id: int
    fee_structure_id: int
    due_date: date
    discount: float = 0
    fine: float = 0
    status: str = 'Unpaid'

class StudentFeeCreate(StudentFeeBase):
    pass

class StudentFeeUpdate(BaseModel):
    discount: Optional[float] = None
    fine: Optional[float] = None
    status: Optional[str] = None

class StudentFeeResponse(StudentFeeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# FeeReceipt
class FeeReceiptBase(BaseModel):
    receipt_number: str
    student_fee_id: int
    amount_paid: float
    payment_date: date
    payment_mode: str

class FeeReceiptCreate(FeeReceiptBase):
    pass

class FeeReceiptResponse(FeeReceiptBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Timetable
class TimetableBase(BaseModel):
    class_id: int
    section_id: int
    subject_id: int
    teacher_id: int
    day_of_week: str
    start_time: str
    end_time: str

class TimetableCreate(TimetableBase):
    pass

class TimetableUpdate(BaseModel):
    teacher_id: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class TimetableResponse(TimetableBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# LeaveRequest
class LeaveRequestBase(BaseModel):
    user_type: str
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    start_date: date
    end_date: date
    reason: str
    status: str = 'Pending'

class LeaveRequestCreate(LeaveRequestBase):
    pass

class LeaveRequestUpdate(BaseModel):
    status: str

class LeaveRequestResponse(LeaveRequestBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Notice
class NoticeBase(BaseModel):
    title: str
    content: str
    publish_date: date
    expiry_date: Optional[date] = None
    is_school_wide: bool = True
    class_id: Optional[int] = None

class NoticeCreate(NoticeBase):
    pass

class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    expiry_date: Optional[date] = None
    is_school_wide: Optional[bool] = None

class NoticeResponse(NoticeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# SchoolSetting
class SchoolSettingBase(BaseModel):
    school_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    academic_year: Optional[str] = None
    principal_name: Optional[str] = None
    logo_url: Optional[str] = None

class SchoolSettingCreate(SchoolSettingBase):
    pass

class SchoolSettingUpdate(BaseModel):
    school_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    academic_year: Optional[str] = None
    principal_name: Optional[str] = None
    logo_url: Optional[str] = None

class SchoolSettingResponse(SchoolSettingBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

