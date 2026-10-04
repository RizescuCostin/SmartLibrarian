import pytest

from smart_librarian.rag.book_ids import create_book_id


@pytest.mark.parametrize(
    ("title", "expected_id"),
    [
        ("1984", "1984"),
        ("The Hobbit", "the-hobbit"),
        (
            "Harry Potter and the Philosopher's Stone",
            "harry-potter-and-the-philosopher-s-stone",
        ),
        ("  Pride and Prejudice  ", "pride-and-prejudice"),
    ],
)
def test_create_book_id(title: str, expected_id: str) -> None:
    assert create_book_id(title) == expected_id


def test_create_book_id_rejects_empty_value() -> None:
    with pytest.raises(ValueError, match="Cannot create a book ID"):
        create_book_id("   ")
