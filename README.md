An AI chatbot that recommends books using semantic retrieval with ChromaDB,
OpenAI models, and function calling.

The application allows a user to describe the kind of book they want in natural language, for example:

"I want a fantasy story with friendship and a lot of adventure."

Smart Librarian searches a local vector database for the most relevant books, asks an OpenAI model to choose the best candidate, retrieves the full summary through a local tool, and returns a structured recommendation.

The application is separated into layers so that each component has one main responsibility.

```text
User
  |
  v
CLI / Streamlit
  |
  v
LibrarianService
  |
  +----------------------+
  |                      |
  v                      |
BookRetriever            |
  |                      |
  v                      |
ChromaVectorStore        |
  |                      |
  v                      |
ChromaDB                 |
  |                      |
  v                      |
Top matching books       |
  |                      |
  +----------+           |
             v           |
         OpenAI LLM      |
             |           |
             v           |
 get_summary_by_title    |
       tool call         |
             |           |
             v           |
        ToolExecutor     |
             |           |
             v           |
       BookRepository    |
             |           |
             v           |
   book_summaries.json   |
             |           |
             v           |
        full summary     |
             |           |
             +-----------+
             |
             v
       Final response
             |
             v
            User
```