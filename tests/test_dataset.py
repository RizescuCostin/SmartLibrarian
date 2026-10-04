from smart_librarian.data.book_repository import BookRepository


def test_main_dataset_contains_at_least_ten_books() -> None:
    repository = BookRepository()

    assert len(repository.get_all()) >= 10


def test_main_dataset_titles_are_not_empty() -> None:
    repository = BookRepository()

    for book in repository.get_all():
        assert book.title
        assert book.short_summary
        assert book.full_summary


def test_main_dataset_books_have_themes_and_genres() -> None:
    repository = BookRepository()

    for book in repository.get_all():
        assert book.themes
        assert book.genres
