from smart_librarian.data.book_repository import BookRepository
from smart_librarian.tools.book_tools import get_summary_by_title


class ToolExecutor:
    """Executes application tools requested by the language model."""

    def __init__(
        self,
        repository: BookRepository,
    ) -> None:
        self._repository = repository

    def execute(
        self,
        *,
        tool_name: str,
        arguments: dict,
    ) -> str:
        """Execute a supported tool and return its result."""

        if tool_name == "get_summary_by_title":
            return get_summary_by_title(
                title=arguments["title"],
                repository=self._repository,
            )

        raise ValueError(f"Unsupported tool: {tool_name}")
