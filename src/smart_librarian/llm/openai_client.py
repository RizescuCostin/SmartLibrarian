import json

from openai import OpenAI

from smart_librarian.domain.librarian_models import LibrarianAnswer
from smart_librarian.domain.recommendation_models import BookRecommendation
from smart_librarian.domain.search_models import BookCandidate
from smart_librarian.llm.prompts import (
    SYSTEM_PROMPT,
    TOOL_RECOMMENDATION_SYSTEM_PROMPT,
    build_recommendation_prompt,
)
from smart_librarian.llm.tool_definitions import GET_SUMMARY_BY_TITLE_TOOL
from smart_librarian.tools.tool_executor import ToolExecutor


class OpenAIRecommendationClient:
    """Uses OpenAI to select one book from retrieved candidates."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
    ) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def recommend(
        self,
        *,
        user_query: str,
        candidates: list[BookCandidate],
    ) -> BookRecommendation:
        """Return one recommendation chosen from retrieved candidates."""

        if not user_query.strip():
            raise ValueError("User query must not be empty.")

        if not candidates:
            raise ValueError("At least one candidate is required.")

        prompt = build_recommendation_prompt(
            user_query=user_query,
            candidates=candidates,
        )

        response = self._client.responses.create(
            model=self._model,
            instructions=SYSTEM_PROMPT,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "book_recommendation",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                            },
                            "reason": {
                                "type": "string",
                            },
                        },
                        "required": [
                            "title",
                            "reason",
                        ],
                        "additionalProperties": False,
                    },
                }
            },
        )

        raw_output = response.output_text
        parsed_output = json.loads(raw_output)

        recommendation = BookRecommendation.model_validate(parsed_output)

        self._validate_recommended_title(
            recommendation=recommendation,
            candidates=candidates,
        )

        return recommendation

    @staticmethod
    def _validate_recommended_title(
        *,
        recommendation: BookRecommendation,
        candidates: list[BookCandidate],
    ) -> None:
        candidate_titles = {candidate.title for candidate in candidates}

        if recommendation.title not in candidate_titles:
            raise ValueError(
                "The model recommended a title that was not "
                "present in the retrieved candidates."
            )

    def recommend_with_summary(
        self,
        *,
        user_query: str,
        candidates: list[BookCandidate],
        tool_executor: ToolExecutor,
    ) -> LibrarianAnswer:
        """Recommend one retrieved book and obtain its local full summary."""

        if not user_query.strip():
            raise ValueError("User query must not be empty.")

        if not candidates:
            raise ValueError("At least one candidate is required.")

        prompt = build_recommendation_prompt(
            user_query=user_query,
            candidates=candidates,
        )

        response = self._client.responses.create(
            model=self._model,
            instructions=TOOL_RECOMMENDATION_SYSTEM_PROMPT,
            input=prompt,
            tools=[GET_SUMMARY_BY_TITLE_TOOL],
        )

        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            raise ValueError("The model did not request get_summary_by_title.")

        if len(tool_calls) > 1:
            raise ValueError("The model requested more than one tool call.")

        tool_call = tool_calls[0]

        if tool_call.name != "get_summary_by_title":
            raise ValueError(f"Unexpected tool requested: {tool_call.name}")

        try:
            arguments = json.loads(tool_call.arguments)
        except json.JSONDecodeError as exc:
            raise ValueError("The model returned invalid tool arguments.") from exc

        requested_title = arguments.get("title")

        if not isinstance(requested_title, str):
            raise ValueError("Tool argument 'title' must be a string.")

        candidate_titles = {candidate.title for candidate in candidates}

        if requested_title not in candidate_titles:
            raise ValueError(
                "The model requested a summary for a book that was not retrieved."
            )

        tool_result = tool_executor.execute(
            tool_name=tool_call.name,
            arguments=arguments,
        )

        final_response = self._client.responses.create(
            model=self._model,
            previous_response_id=response.id,
            input=[
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": tool_result,
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "librarian_answer",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                            },
                            "reason": {
                                "type": "string",
                            },
                            "summary": {
                                "type": "string",
                            },
                        },
                        "required": [
                            "title",
                            "reason",
                            "summary",
                        ],
                        "additionalProperties": False,
                    },
                }
            },
        )
        raw_output = final_response.output_text
        parsed_output = json.loads(raw_output)

        answer = LibrarianAnswer.model_validate(parsed_output)

        if answer.title != requested_title:
            raise ValueError(
                "The final response title does not match "
                "the book used in the summary tool call."
            )

        if answer.summary.strip() != tool_result.strip():
            raise ValueError(
                "The final response changed the summary returned by the local tool."
            )

        return answer
