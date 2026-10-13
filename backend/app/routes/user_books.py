
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.book import Book
from backend.app.models.user import User
from backend.app.models.user_book import UserBook
from backend.app.schemas.book import AddBookToLibrary, UserBookUpdate
from backend.app.services.book_search import get_edition_details


router = APIRouter(
    prefix="/user-books",
    tags=["user-books"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
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

    # 4. Create the shared book record if it doesn't exist.
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

    # 5. Prevent duplicate library entries.
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


@router.get("/")
def get_user_library(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    # 1. Make sure the user exists.
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 2. Find the user's library entries.
    statement = (
        select(UserBook, Book)
        .join(Book, UserBook.book_id == Book.id)
        .where(UserBook.user_id == user_id)
        .order_by(UserBook.created_at.desc())
    )

    results = db.execute(statement).all()

    # 3. Format the results for the API response.
    library = []

    for user_book, book in results:
        library.append({
            "user_book_id": str(user_book.id),
            "book_id": str(book.id),
            "title": book.title,
            "cover_url": book.cover_url,
            "status": user_book.status,
            "progress_pages": user_book.progress_pages,
            "progress_percent": float(user_book.progress_percent),
            "started_at": user_book.started_at,
            "finished_at": user_book.finished_at,
            "dnf_at_percent": (
                float(user_book.dnf_at_percent)
                if user_book.dnf_at_percent is not None
                else None
            ),
            "dnf_reason": user_book.dnf_reason,
        })

    return library


@router.patch("/{user_book_id}")
def update_user_book(
    user_book_id: UUID,
    request: UserBookUpdate,
    db: Session = Depends(get_db),
):
    # 1. Find the user's library entry.
    user_book = db.get(UserBook, user_book_id)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in user's library",
        )

    book = db.get(Book, user_book.book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book record not found",
        )

    # 2. Get only the fields the client actually sent.
    updates = request.model_dump(exclude_unset=True)

    # 3. Validate progress and synchronize pages and percentage.
    if "progress_pages" in updates:
        if updates["progress_pages"] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pages read cannot be null",
            )

        if book.page_count is None or book.page_count <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Cannot calculate progress because the "
                    "book's page count is unknown"
                ),
            )

        if updates["progress_pages"] > book.page_count:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pages read cannot exceed the book's total page count",
            )

        # Pages take precedence if both progress fields are supplied.
        updates["progress_percent"] = (
            updates["progress_pages"] / book.page_count
        ) * 100

    elif "progress_percent" in updates:
        if updates["progress_percent"] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Progress percentage cannot be null",
            )

        if book.page_count is None or book.page_count <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Cannot calculate pages because the "
                    "book's page count is unknown"
                ),
            )

        # Round to the nearest whole page, with halves rounded up.
        updates["progress_pages"] = int(
            book.page_count * updates["progress_percent"] / 100 + 0.5
        )

    # 4. Prevent status from being set to null.
    if "status" in request.model_fields_set and request.status is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Status cannot be null",
        )

    # 5. Apply the requested changes.
    for field, value in updates.items():
        setattr(user_book, field, value)

    # 6. Record when the user starts reading.
    if user_book.status == "Currently Reading":
        if user_book.started_at is None:
            user_book.started_at = datetime.now(timezone.utc)

    # 7. Handle completed books and finish timestamps.
    if user_book.status == "Read":
        user_book.progress_percent = 100

        if book.page_count is not None and book.page_count > 0:
            user_book.progress_pages = book.page_count

        if user_book.finished_at is None:
            user_book.finished_at = datetime.now(timezone.utc)
    else:
        user_book.finished_at = None

    # 8. Handle DNF information.
    if user_book.status == "DNF'd":
        if "dnf_at_percent" in updates:
            user_book.dnf_at_percent = updates["dnf_at_percent"]
        else:
            user_book.dnf_at_percent = user_book.progress_percent
    else:
        user_book.dnf_at_percent = None
        user_book.dnf_reason = None

    # 9. Save the changes to the database.
    try:
        db.commit()
        db.refresh(user_book)
    except Exception as e:
        db.rollback()
        print(f"Error updating user book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update the book",
        )

    # 10. Return the updated entry.
    return {
        "user_book_id": str(user_book.id),
        "book_id": str(user_book.book_id),
        "status": user_book.status,
        "progress_pages": user_book.progress_pages,
        "progress_percent": float(user_book.progress_percent),
        "started_at": user_book.started_at,
        "finished_at": user_book.finished_at,
        "dnf_at_percent": (
            float(user_book.dnf_at_percent)
            if user_book.dnf_at_percent is not None
            else None
        ),
        "dnf_reason": user_book.dnf_reason,
    }