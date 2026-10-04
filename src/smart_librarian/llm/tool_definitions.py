GET_SUMMARY_BY_TITLE_TOOL = {
    "type": "function",
    "name": "get_summary_by_title",
    "description": (
        "Returns the complete local summary for a recommended book. "
        "The title must exactly match one of the available book titles."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": ("The exact title of the recommended book."),
            },
        },
        "required": ["title"],
        "additionalProperties": False,
    },
    "strict": True,
}
