from fastapi import FastAPI
from sqlalchemy import text

from .database import engine
from . import models
from .routes import (
    students,
    attendance,
    classes,
    sections,
)


# ------------------------------------------------------------
# FastAPI application
# ------------------------------------------------------------

app = FastAPI(
    title="Student Management API",
    description="Backend API for School Student Management System",
    version="1.0.0",
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