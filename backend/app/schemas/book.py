from typing import List, Literal
from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    subtitle: str | None = None
    description: str | None = None
    isbn_10: str | None = None
    isbn_13: str | None = None
    publisher: str | None = None
    published_date: date | None = None
    page_count: int | None = Field(default=None, ge=0)
    cover_url: str | None = None
    source: str | None = None
    source_id: str | None = None


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    subtitle: str | None = None
    description: str | None = None
    isbn_10: str | None = None
    isbn_13: str | None = None
    publisher: str | None = None
    published_date: date | None = None
    page_count: int | None = None
    cover_url: str | None = None
    source: str | None = None
    source_id: str | None = None

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    subtitle: str | None = None
    description: str | None = None
    isbn_10: str | None = None
    isbn_13: str | None = None
    publisher: str | None = None
    published_date: date | None = None
    page_count: int | None = Field(default=None, ge=0)
    cover_url: str | None = None
    source: str | None = None
    source_id: str | None = None

class BookSearchResult(BaseModel):
    title: str | None = None
    authors: list[str] = []
    isbn_10: str | None = None
    published_year: int | None = None
    publisher: str | None = None
    cover_url: str | None = None
    source: str
    source_id: str | None = None


class BookEditionDetail(BaseModel):
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    isbn_10: str | None = None
    isbn_13: str | None = None
    published_year: int | None = None
    published_date: str | None = None
    publisher: str | None = None
    page_count: int | None = Field(default=None, ge=0)
    cover_url: str | None = None
    source: str
    source_id: str | None = None


class AddBookToLibrary(BaseModel):
    user_id: UUID
    edition_id: str = Field(min_length=1)
    status: Literal[
    "Want to Read",
    "Currently Reading",
    "Read",
    "On Hold",
    "DNF'd",
    "Re-read",
    "Re-reading",
] = "Want to Read"

class UserBookUpdate(BaseModel):
    status: Literal[
        "Want to Read",
        "Currently Reading",
        "Read",
        "On Hold",
        "DNF'd",
        "Re-read",
        "Re-reading",
    ] | None = None

    progress_pages: int | None = Field(default=None, ge=0)
    progress_percent: float | None = Field(default=None, ge=0, le=100)
    dnf_at_percent: float | None = Field(default=None, ge=0, le=100)
    dnf_reason: str | None = None
    