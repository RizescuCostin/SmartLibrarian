import html

import streamlit as st

from smart_librarian.config import get_settings
from smart_librarian.data.book_repository import BookRepository
from smart_librarian.llm.openai_client import OpenAIRecommendationClient
from smart_librarian.llm.speech_client import OpenAISpeechClient
from smart_librarian.llm.transcription_client import OpenAITranscriptionClient
from smart_librarian.rag.retriever import BookRetriever
from smart_librarian.rag.vector_store import ChromaVectorStore
from smart_librarian.services.librarian_service import LibrarianService
from smart_librarian.tools.tool_executor import ToolExecutor

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Smart Librarian",
    page_icon="📚",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Application dependencies
# ---------------------------------------------------------------------------

@st.cache_resource
def create_service() -> LibrarianService:
    """Create and cache the Smart Librarian service."""

    settings = get_settings()

    repository = BookRepository()

    vector_store = ChromaVectorStore(
        persist_directory=settings.chroma_persist_directory,
        collection_name=settings.chroma_collection_name,
    )

    retriever = BookRetriever(vector_store)

    recommendation_client = OpenAIRecommendationClient(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
    )

    tool_executor = ToolExecutor(repository)

    return LibrarianService(
        retriever=retriever,
        recommendation_client=recommendation_client,
        tool_executor=tool_executor,
    )


@st.cache_resource
def create_transcription_client() -> OpenAITranscriptionClient:
    """Create and cache the speech-to-text client."""

    settings = get_settings()

    return OpenAITranscriptionClient(
        api_key=settings.openai_api_key,
    )


@st.cache_resource
def create_speech_client() -> OpenAISpeechClient:
    """Create and cache the text-to-speech client."""

    settings = get_settings()

    return OpenAISpeechClient(
        api_key=settings.openai_api_key,
    )


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .subtitle {
            text-align: center;
            color: #777;
            margin-bottom: 2rem;
        }

        .panel-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }

        .message-box {
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba(128, 128, 128, 0.3);
            margin-bottom: 0.75rem;
        }

        .loading-books {
            display: flex;
            justify-content: center;
            gap: 12px;
            font-size: 2rem;
            padding: 2rem 2rem 0.5rem;
        }

        .loading-books span {
            display: inline-block;
            animation: bounce 0.8s infinite alternate;
        }

        .loading-books span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .loading-books span:nth-child(3) {
            animation-delay: 0.4s;
        }

        .loading-text {
            text-align: center;
            margin-bottom: 1rem;
            color: #777;
        }

        @keyframes bounce {
            from {
                transform: translateY(0);
            }

            to {
                transform: translateY(-15px);
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "queries" not in st.session_state:
    st.session_state.queries = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "audio_results" not in st.session_state:
    st.session_state.audio_results = {}


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="main-title">📚 Smart Librarian</div>',
    unsafe_allow_html=True,
)

st.markdown(
    (
        '<div class="subtitle">'
        "Tell me what kind of book you're looking for — "
        "by typing or speaking."
        "</div>"
    ),
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Query and response history
# ---------------------------------------------------------------------------

left_column, right_column = st.columns(
    2,
    gap="large",
)


with left_column:
    st.markdown(
        '<div class="panel-title">🔎 Your requests</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.queries:
        st.caption(
            "Your requests will appear here."
        )

    for query in st.session_state.queries:
        safe_query = html.escape(query)

        st.markdown(
            f'<div class="message-box">{safe_query}</div>',
            unsafe_allow_html=True,
        )


with right_column:
    st.markdown(
        '<div class="panel-title">📖 Librarian responses</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.answers:
        st.caption(
            "Book recommendations will appear here."
        )

    for index, answer in enumerate(
        st.session_state.answers
    ):
        with st.container(border=True):
            st.subheader(
                f"📕 {answer['title']}"
            )

            st.write(
                answer["reason"]
            )

            with st.expander(
                "Read full summary"
            ):
                st.write(
                    answer["summary"]
                )

            # ---------------------------------------------------------------
            # Text-to-speech
            # ---------------------------------------------------------------

            audio_key = f"answer-{index}"

            if st.button(
                "🔊 Listen",
                key=f"listen-{index}",
            ):
                try:
                    if (
                        audio_key
                        not in st.session_state.audio_results
                    ):
                        with st.spinner(
                            "Preparing audio..."
                        ):
                            speech_client = (
                                create_speech_client()
                            )

                            speech_text = (
                                f"I recommend "
                                f"{answer['title']}. "
                                f"{answer['reason']} "
                                f"{answer['summary']}"
                            )

                            audio = (
                                speech_client.synthesize(
                                    speech_text
                                )
                            )

                            st.session_state.audio_results[
                                audio_key
                            ] = audio.getvalue()

                except Exception as exc:
                    st.error(
                        f"Could not generate speech: {exc}"
                    )

            if (
                audio_key
                in st.session_state.audio_results
            ):
                st.audio(
                    st.session_state.audio_results[
                        audio_key
                    ],
                    format="audio/mp3",
                )

# ---------------------------------------------------------------------------
# Query input
# ---------------------------------------------------------------------------

st.divider()

st.markdown(
    "### Find your next book"
)


with st.form(
    "book_query_form",
    clear_on_submit=True,
):
    user_query = st.text_input(
        "What are you looking for?",
        placeholder=(
            "For example: I want a fantasy book "
            "with friendship and adventure..."
        ),
    )

    recorded_audio = st.audio_input(
        "Or speak your request 🎙️",
        sample_rate=16000,
    )

    submitted = st.form_submit_button(
        "Find me a book 🔎",
        use_container_width=True,
    )


# ---------------------------------------------------------------------------
# Process query
# ---------------------------------------------------------------------------

if submitted:
    normalized_query = user_query.strip()

    # -----------------------------------------------------------------------
    # Speech-to-text
    # -----------------------------------------------------------------------

    if not normalized_query and recorded_audio is not None:
        try:
            with st.spinner(
                "🎙️ Transcribing your request..."
            ):
                transcription_client = (
                    create_transcription_client()
                )

                normalized_query = (
                    transcription_client.transcribe(
                        recorded_audio
                    )
                )

            if normalized_query:
                st.info(
                    f'🎙️ I heard: "{normalized_query}"'
                )

        except Exception as exc:
            st.error(
                f"Could not transcribe audio: {exc}"
            )

    # -----------------------------------------------------------------------
    # Validate input
    # -----------------------------------------------------------------------

    if not normalized_query:
        st.warning(
            "Please type or record what kind of "
            "book you're looking for."
        )

    else:
        # -------------------------------------------------------------------
        # Recommendation loading animation
        # -------------------------------------------------------------------

        loading_placeholder = st.empty()

        loading_placeholder.markdown(
            """
            <div class="loading-books">
                <span>📕</span>
                <span>📗</span>
                <span>📘</span>
            </div>

            <div class="loading-text">
                Searching the library...
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            service = create_service()

            answer = service.answer(
                normalized_query
            )

            # ---------------------------------------------------------------
            # Save query
            # ---------------------------------------------------------------

            st.session_state.queries.append(
                normalized_query
            )

            # ---------------------------------------------------------------
            # Save recommendation
            # ---------------------------------------------------------------

            st.session_state.answers.append(
                {
                    "title": answer.title,
                    "reason": answer.reason,
                    "summary": answer.summary,
                }
            )

        except Exception as exc:
            st.error(
                f"Something went wrong: {exc}"
            )

        finally:
            loading_placeholder.empty()

        st.rerun()