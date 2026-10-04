from io import BytesIO

from openai import OpenAI


class OpenAISpeechClient:
    """Converts text into spoken audio."""

    def __init__(self, *, api_key: str) -> None:
        self._client = OpenAI(api_key=api_key)

    def synthesize(self, text: str) -> BytesIO:
        """Return MP3 audio containing spoken text."""

        if not text.strip():
            raise ValueError("Speech text must not be empty.")

        response = self._client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="mp3",
        )

        audio_buffer = BytesIO(response.content)
        audio_buffer.seek(0)

        return audio_buffer