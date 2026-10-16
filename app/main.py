from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import engine
from . import models
from .routes import (
    students,
    attendance,
    classes,
    sections,
    auth,
    users,
    teachers,
    subjects,
    assignments,
    parents,
    exams,
    results,
    fees,
    receipts,
    timetables,
    leaves,
    notices,
    settings,
)


# ------------------------------------------------------------
# FastAPI application
# ------------------------------------------------------------

app = FastAPI(
    title="Student Management API",
    description="Backend API for School Student Management System",
    version="1.0.0",
)

# Create all tables on startup if they do not exist
models.Base.metadata.create_all(bind=engine)

# Ensure default admin exists
try:
    from .database import SessionLocal
    from .models import User, UserRole
    from .auth import get_password_hash
    with SessionLocal() as db:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                email="admin@school.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            ))
            db.commit()
except Exception as e:
    pass


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# Root endpoint
# ------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Student Management API is running"
    }


# ------------------------------------------------------------
# Database connection test
# ------------------------------------------------------------

@app.get("/db-test")
def database_test():
    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            value = result.scalar()

        return {
            "database": "connected",
            "test": value
        }

    except Exception as error:

        return {
            "database": "connection failed",
            "error": str(error)
        }


# ------------------------------------------------------------
# API Routers
# ------------------------------------------------------------

app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(classes.router)
app.include_router(sections.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(teachers.router)
app.include_router(subjects.router)
app.include_router(assignments.router)
app.include_router(parents.router)
app.include_router(exams.router)
app.include_router(results.router)
app.include_router(fees.router)
app.include_router(receipts.router)
app.include_router(timetables.router)
app.include_router(leaves.router)
app.include_router(notices.router)
app.include_router(settings.router)
