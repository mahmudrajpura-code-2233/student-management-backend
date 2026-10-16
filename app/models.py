from sqlalchemy import Integer, String, Boolean, ForeignKey, Date, DateTime, UniqueConstraint, Float, Text
from datetime import date
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


# ============================================================
# SCHOOL CLASS MODEL
# ============================================================

class SchoolClass(Base):

    __tablename__ = "school_classes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )


# ============================================================
# SECTION MODEL
# ============================================================

class Section(Base):

    __tablename__ = "sections"
    __table_args__ = (
        UniqueConstraint("class_id", "name", name="uq_class_section"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    class_id: Mapped[int] = mapped_column(
        ForeignKey("school_classes.id"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )


# ============================================================
# STUDENT MODEL
# ============================================================

class Student(Base):

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    student_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # --------------------------------------------------------
    # CLASS FOREIGN KEY
    # --------------------------------------------------------

    class_id: Mapped[int] = mapped_column(
        ForeignKey("school_classes.id"),
        nullable=False,
        index=True
    )

    # --------------------------------------------------------
    # SECTION FOREIGN KEY
    # --------------------------------------------------------

    section_id: Mapped[int] = mapped_column(
        ForeignKey("sections.id"),
        nullable=False,
        index=True
    )

    roll_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    gr_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    father_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mother_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    primary_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    secondary_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    aadhaar_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_yearly_fees: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    school_class: Mapped["SchoolClass"] = relationship(
        foreign_keys=[class_id]
    )

    section_obj: Mapped["Section"] = relationship(
        foreign_keys=[section_id]
    )

    attendance: Mapped[list["Attendance"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan"
    )


# ============================================================
# ATTENDANCE MODEL
# ============================================================

class Attendance(Base):

    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("student_id", "attendance_date", name="uq_student_attendance_date"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        index=True
    )

    attendance_date: Mapped[Date] = mapped_column(
        Date,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    remarks: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # --------------------------------------------------------
    # CREATED AT
    # --------------------------------------------------------

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIP
    # --------------------------------------------------------

    student: Mapped["Student"] = relationship(
        back_populates="attendance"
    )

# ============================================================
# USER ROLE ENUM
# ============================================================
import enum

class UserRole(str, enum.Enum):
    ADMIN = 'Admin'
    TEACHER = 'Teacher'
    STAFF = 'Staff'

# ============================================================
# USER MODEL
# ============================================================

class User(Base):

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(20), nullable=False, default=UserRole.STAFF)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


# ============================================================
# TEACHER MODEL
# ============================================================

class Teacher(Base):
    __tablename__ = 'teachers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True) # Optional link to auth user
    teacher_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    mobile: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    qualification: Mapped[str] = mapped_column(String(100), nullable=True)
    joining_date: Mapped[Date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

# ============================================================
# SUBJECT MODEL
# ============================================================

class Subject(Base):
    __tablename__ = 'subjects'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False)
    subject_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

# ============================================================
# ASSIGNMENT MODEL
# ============================================================

class TeacherAssignment(Base):
    __tablename__ = 'teacher_assignments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey('school_classes.id'), nullable=False)
    section_id: Mapped[int | None] = mapped_column(ForeignKey('sections.id'), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

# ============================================================
# PARENT MODEL
# ============================================================

class Parent(Base):
    __tablename__ = 'parents'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), unique=True, nullable=False)
    father_name: Mapped[str] = mapped_column(String(100), nullable=True)
    mother_name: Mapped[str] = mapped_column(String(100), nullable=True)
    guardian_name: Mapped[str] = mapped_column(String(100), nullable=True)
    mobile: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    relation_to_student: Mapped[str] = mapped_column(String(50), nullable=True)

# ============================================================
# EXAM MODEL
# ============================================================

class Exam(Base):
    __tablename__ = 'exams'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exam_name: Mapped[str] = mapped_column(String(100), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    exam_date: Mapped[Date] = mapped_column(Date, nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey('school_classes.id'), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)
    total_marks: Mapped[int] = mapped_column(Integer, nullable=False)
    passing_marks: Mapped[int] = mapped_column(Integer, nullable=False)

# ============================================================
# EXAM RESULT MODEL
# ============================================================

class ExamResult(Base):
    __tablename__ = 'exam_results'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey('exams.id'), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), nullable=False)
    obtained_marks: Mapped[float] = mapped_column(Integer, nullable=False) # wait float or int? Int is fine for now but let's just make it float later
    percentage: Mapped[float] = mapped_column(Integer, nullable=True)
    grade: Mapped[str] = mapped_column(String(5), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=True) # Pass/Fail
    rank: Mapped[int] = mapped_column(Integer, nullable=True)
    __table_args__ = (UniqueConstraint('exam_id', 'student_id', name='uq_exam_student'),)

# ============================================================
# FEE STRUCTURE MODEL
# ============================================================

class FeeStructure(Base):
    __tablename__ = 'fee_structures'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey('school_classes.id'), nullable=False)
    fee_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Integer, nullable=False)

# ============================================================
# STUDENT FEE RECORD MODEL
# ============================================================

class StudentFee(Base):
    __tablename__ = 'student_fees'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), nullable=False)
    fee_structure_id: Mapped[int] = mapped_column(ForeignKey('fee_structures.id'), nullable=False)
    due_date: Mapped[Date] = mapped_column(Date, nullable=False)
    discount: Mapped[float] = mapped_column(Integer, default=0)
    fine: Mapped[float] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default='Unpaid') # Unpaid, Partial, Paid

# ============================================================
# FEE RECEIPT MODEL
# ============================================================

class FeeReceipt(Base):
    __tablename__ = 'fee_receipts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    receipt_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    student_fee_id: Mapped[int] = mapped_column(ForeignKey('student_fees.id'), nullable=False)
    amount_paid: Mapped[float] = mapped_column(Integer, nullable=False)
    payment_date: Mapped[Date] = mapped_column(Date, nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(50), nullable=False)

# ============================================================
# TIMETABLE MODEL
# ============================================================

class Timetable(Base):
    __tablename__ = 'timetables'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey('school_classes.id'), nullable=False)
    section_id: Mapped[int] = mapped_column(ForeignKey('sections.id'), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[str] = mapped_column(String(10), nullable=False)
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)

# ============================================================
# LEAVE REQUEST MODEL
# ============================================================

class LeaveRequest(Base):
    __tablename__ = 'leave_requests'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_type: Mapped[str] = mapped_column(String(20), nullable=False) # 'Student' or 'Teacher/Staff'
    student_id: Mapped[int | None] = mapped_column(ForeignKey('students.id'), nullable=True)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey('teachers.id'), nullable=True)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='Pending') # Pending, Approved, Rejected

# ============================================================
# NOTICE MODEL
# ============================================================

class Notice(Base):
    __tablename__ = 'notices'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    publish_date: Mapped[Date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Date] = mapped_column(Date, nullable=True)
    is_school_wide: Mapped[bool] = mapped_column(Boolean, default=True)
    class_id: Mapped[int | None] = mapped_column(ForeignKey('school_classes.id'), nullable=True)

# ============================================================
# SCHOOL SETTING MODEL
# ============================================================

class SchoolSetting(Base):
    __tablename__ = 'school_settings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    school_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    website: Mapped[str] = mapped_column(String(100), nullable=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=True)
    principal_name: Mapped[str] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)

