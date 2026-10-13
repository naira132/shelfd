
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.book import Book
from backend.app.models.user import User
from backend.app.models.user_book import UserBook
from backend.app.schemas.book import AddBookToLibrary, BookResponse
from backend.app.services.book_search import get_edition_details


router = APIRouter(
    prefix="/user-books",
    tags=["user-books"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
def add_book_to_library(
    request: AddBookToLibrary,
    db: Session = Depends(get_db),
):
    # 1. Make sure the user exists.
    user = db.get(User, request.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 2. Retrieve the selected edition from Open Library.
    try:
        edition = get_edition_details(request.edition_id)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Book edition service is temporarily unavailable",
        )

    if not edition.get("title"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book edition not found",
        )

    # 3. Find the edition in our books table.
    book_statement = select(Book).where(
        Book.source == edition["source"],
        Book.source_id == edition["source_id"],
    )
    book = db.scalar(book_statement)

    # 4. If it doesn't exist, create the shared book record.
    if book is None:
        book = Book(
            title=edition["title"],
            isbn_10=edition.get("isbn_10"),
            isbn_13=edition.get("isbn_13"),
            publisher=edition.get("publisher"),
            page_count=edition.get("page_count"),
            cover_url=edition.get("cover_url"),
            source=edition["source"],
            source_id=edition["source_id"],
        )

        db.add(book)
        db.flush()

    # 5. Check whether this user already has this book.
    user_book_statement = select(UserBook).where(
        UserBook.user_id == request.user_id,
        UserBook.book_id == book.id,
    )
    user_book = db.scalar(user_book_statement)

    if user_book is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This book is already in the user's library",
        )

    # 6. Create the user's library entry.
    user_book = UserBook(
        user_id=request.user_id,
        book_id=book.id,
        status=request.status,
        progress_pages=0,
        progress_percent=0,
    )

    db.add(user_book)

    try:
        db.commit()
        db.refresh(user_book)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not add the book to the user's library",
        )

    return {
        "message": "Book added to library",
        "book_id": str(book.id),
        "user_book_id": str(user_book.id),
        "title": book.title,
        "status": user_book.status,
    }