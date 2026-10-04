from pathlib import Path

import pytest

from smart_librarian.data.book_repository import BookRepository
from smart_librarian.tools.tool_executor import ToolExecutor

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"
SAMPLE_BOOKS_FILE = FIXTURES_DIRECTORY / "sample_books.json"


@pytest.fixture
def executor() -> ToolExecutor:
    repository = BookRepository(SAMPLE_BOOKS_FILE)
    return ToolExecutor(repository)


def test_executor_runs_summary_tool(
    executor: ToolExecutor,
) -> None:
    result = executor.execute(
        tool_name="get_summary_by_title",
        arguments={
            "title": "Test Book One",
        },
    )

    assert result == ("A complete summary for the first test book.")


def test_executor_rejects_unknown_tool(
    executor: ToolExecutor,
) -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported tool",
    ):
        executor.execute(
            tool_name="destroy_the_world",
            arguments={},
        )


def test_executor_rejects_missing_title(
    executor: ToolExecutor,
) -> None:
    with pytest.raises(KeyError):
        executor.execute(
            tool_name="get_summary_by_title",
            arguments={},
        )
