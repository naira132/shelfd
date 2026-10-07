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