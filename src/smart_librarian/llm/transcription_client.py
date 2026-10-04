from openai import OpenAI


class OpenAITranscriptionClient:
    """Transcribes recorded speech into text."""

    def __init__(self, *, api_key: str) -> None:
        self._client = OpenAI(api_key=api_key)

    def transcribe(self, audio_file) -> str:
        """Return the transcript for recorded audio."""

        transcription = self._client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file,
        )

        return transcription.text.strip()