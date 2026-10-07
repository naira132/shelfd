from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.book import Book
from backend.app.schemas.book import (
    BookCreate,
    BookResponse,
    BookSearchResult,
    BookUpdate,
)
from backend.app.services.book_search import search_books

router = APIRouter(
    prefix="/books",
    tags=["books"],
)


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
):
    book = Book(**book_data.model_dump())

    db.add(book)
    db.commit()
    db.refresh(book)

    return book
@router.get(
    "/",
    response_model=list[BookResponse],
)
def get_books(
    db: Session = Depends(get_db),
):
    books = db.scalars(select(Book)).all()
    return books

@router.get(
    "/search",
    response_model=list[BookSearchResult],
)
def search_books_endpoint(q: str):
    try:
        return search_books(q)
    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="Book search service is temporarily unavailable",
        )
        
@router.get(
    "/{book_id}",
    response_model=BookResponse,
    responses={404: {"description": "Book not found"}},
)
def get_book(
    book_id: UUID,
    db: Session = Depends(get_db),
):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )
    return book

@router.put(
    "/{book_id}",
    response_model=BookResponse,
    responses={404: {"description": "Book not found"}}
)
def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    for field, value in book_data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)

    return book

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Book not found"}}
)
def delete_book(
    book_id: UUID,
    db: Session = Depends(get_db),
):
    book = db.get(Book, book_id)

    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    db.delete(book)
    db.commit()