import httpx


OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"

def search_books(query: str):
    try:
        response = httpx.get(
            OPEN_LIBRARY_SEARCH_URL,
            params={
                "q": query,
                "limit": 10,
            },
            timeout=10.0,
        )

        response.raise_for_status()

    except httpx.HTTPError as exc:
        raise RuntimeError("Book search service is unavailable") from exc

    data = response.json()

    return [
        normalize_book(doc)
        for doc in data.get("docs", [])
    ]

def normalize_book(doc: dict):
    return {
        "title": doc.get("title"),
        "authors": doc.get("author_name", []),
        "isbn_10": doc.get("isbn", [])[0] if doc.get("isbn") else None,
        "published_year": doc.get("first_publish_year"),
        "publisher": doc.get("publisher", [None])[0],
        "cover_url": (
            f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg"
            if doc.get("cover_i")
            else None
        ),
        "source": "openlibrary",
        "source_id": doc.get("key"),
    }


def get_edition_details(edition_id: str):
    edition_key = edition_id.strip("/")

    if edition_key.startswith("books/"):
        edition_key = edition_key.removeprefix("books/")

    url = f"https://openlibrary.org/books/{edition_key}.json"

    try:
        response = httpx.get(
            url,
            timeout=10.0,
        )
        response.raise_for_status()

    except httpx.HTTPError as exc:
        raise RuntimeError(
            "Book edition service is unavailable"
        ) from exc

    data = response.json()

    return normalize_edition(data)


def normalize_edition(data: dict):
    publish_date = data.get("publish_date")
    published_year = None

    if publish_date:
        import re

        match = re.search(r"\b\d{4}\b", publish_date)
        if match:
            published_year = int(match.group())

    isbn_13 = data.get("isbn_13") or []
    isbn_10 = data.get("isbn_10") or []
    publishers = data.get("publishers") or []
    covers = data.get("covers") or []

    return {
        "title": data.get("title"),
        "authors": [],
        "isbn_10": isbn_10[0] if isbn_10 else None,
        "isbn_13": isbn_13[0] if isbn_13 else None,
        "published_year": published_year,
        "published_date": publish_date,
        "publisher": publishers[0] if publishers else None,
        "page_count": data.get("number_of_pages"),
        "cover_url": (
            f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg"
            if covers
            else None
        ),
        "source": "openlibrary",
        "source_id": data.get("key"),
    }