import re
import unicodedata


def create_book_id(title: str) -> str:
    """Create a stable Chroma record ID from a book title."""

    normalized_title = unicodedata.normalize("NFKD", title)
    ascii_title = normalized_title.encode("ascii", "ignore").decode("ascii")
    lowercase_title = ascii_title.casefold()

    slug = re.sub(r"[^a-z0-9]+", "-", lowercase_title)
    slug = slug.strip("-")

    if not slug:
        raise ValueError("Cannot create a book ID from an empty title.")

    return slug
