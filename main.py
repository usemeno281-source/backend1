import os
from contextlib import contextmanager
from typing import Iterator
from uuid import UUID

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row

from app.models import Issue, IssueCreate

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing. Check your .env file.")

app = FastAPI(
    title="Urban Infrastructure Priority Engine",
    description="Backend API for the OFFGRID smart-city hackathon project.",
    version="0.2.0",
    docs_url="/docs",
)


def get_allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    app_env = os.getenv("APP_ENV", "development").lower()

    if app_env == "production":
        return [origin for origin in origins if origin != "*"]

    if origins:
        return origins

    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    with psycopg.connect(
        DATABASE_URL,
        connect_timeout=10,
        sslmode="require",
        row_factory=dict_row,
    ) as connection:
        yield connection


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Urban Infrastructure Priority Engine API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/issues", status_code=201, response_model=Issue)
def create_issue(payload: IssueCreate) -> Issue:
    query = """
        INSERT INTO public.issues (
            issue_type,
            subcategory,
            location,
            description,
            severity,
            population_impact,
            duration
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING
            id, issue_type, subcategory, location, description,
            severity, population_impact, duration, status,
            created_at, priority_score
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        payload.issue_type.value,
                        payload.subcategory,
                        payload.location,
                        payload.description,
                        payload.severity,
                        payload.population_impact,
                        payload.duration,
                    ),
                )
                row = cursor.fetchone()
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database operation failed. Please try again later.",
        )

    return Issue.model_validate(row)


@app.get("/issues", response_model=list[Issue])
def list_issues() -> list[Issue]:
    query = """
        SELECT
            id, issue_type, subcategory, location, description,
            severity, population_impact, duration, status,
            created_at, priority_score
        FROM public.issues
        ORDER BY created_at DESC
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database operation failed. Please try again later.",
        )

    return [Issue.model_validate(row) for row in rows]


@app.get("/issues/{issue_id}", response_model=Issue)
def get_issue(issue_id: UUID) -> Issue:
    query = """
        SELECT
            id, issue_type, subcategory, location, description,
            severity, population_impact, duration, status,
            created_at, priority_score
        FROM public.issues
        WHERE id = %s
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (issue_id,))
                row = cursor.fetchone()
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database operation failed. Please try again later.",
        )

    if row is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    return Issue.model_validate(row)
