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