from sqlalchemy import Integer, String, Boolean, ForeignKey, Date, DateTime
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
        nullable=False
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

    remarks: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    student: Mapped["Student"] = relationship(
        back_populates="attendance"
    )