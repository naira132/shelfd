from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from .user import User
from .book import Book
from .author import Author
from .book_author import BookAuthor