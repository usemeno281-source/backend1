from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class IssueType(str, Enum):
    roadways = "Roadways"
    drainage = "Drainage"
    electricity = "Electricity"
    user_defined = "User-Defined Complaint"


class IssueStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class IssueCreate(BaseModel):
    issue_type: IssueType
    subcategory: str = Field(min_length=1)
    location: str = Field(min_length=1)
    description: str = Field(min_length=1)
    severity: int = Field(ge=1, le=5)
    population_impact: int = Field(ge=1, le=5)
    duration: int = Field(ge=1, le=5)

    @field_validator("subcategory", "location", "description")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty")
        return cleaned


class Issue(BaseModel):
    id: UUID
    issue_type: IssueType
    subcategory: str
    location: str
    description: str
    severity: int
    population_impact: int
    duration: int
    status: IssueStatus = IssueStatus.open
    created_at: datetime
    priority_score: float | None = None
