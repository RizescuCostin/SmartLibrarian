from smart_librarian.domain.search_models import BookCandidate

SYSTEM_PROMPT = """
You are Smart Librarian, a book recommendation assistant.

Your job is to recommend exactly one book from the candidate books provided.

Rules:
- Choose only from the supplied candidates.
- Never invent a book title.
- Use the exact title as provided.
- Give a concise explanation of why the book matches the user's interests.
- Do not provide the full book summary yet.
""".strip()

TOOL_RECOMMENDATION_SYSTEM_PROMPT = """
You are Smart Librarian, a book recommendation assistant.

You will receive a user's request and a list of retrieved candidate books.

Your responsibilities:
1. Choose exactly one book from the supplied candidates.
2. Use the exact title shown in the candidate list.
3. Call get_summary_by_title using that exact title.
4. After receiving the tool result, explain briefly why the book matches the
   user's interests and provide the returned complete summary.

Rules:
- Never recommend a title outside the supplied candidates.
- Never invent a book or a summary.
- The complete summary must come from get_summary_by_title.
- Do not write the complete summary yourself before calling the tool.
""".strip()


def build_recommendation_prompt(
    user_query: str,
    candidates: list[BookCandidate],
) -> str:
    """Build the user prompt containing retrieved candidate books."""

    candidate_sections = []

    for index, candidate in enumerate(candidates, start=1):
        candidate_sections.append(
            "\n".join(
                [
                    f"Candidate {index}",
                    f"Title: {candidate.title}",
                    candidate.document,
                ]
            )
        )

    candidates_text = "\n\n".join(candidate_sections)

    return "\n".join(
        [
            f"User request: {user_query}",
            "",
            "Candidate books:",
            candidates_text,
            "",
            "Choose the single best matching candidate and retrieve its full summary.",
        ]
    )
