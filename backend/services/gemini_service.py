import os

from google import genai

_client: genai.Client | None = None

INTERLEAVED_MODEL = "gemini-2.0-flash-exp-image-generation"
TEXT_MODEL = "gemini-2.5-flash"


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY environment variable is not set")
        _client = genai.Client(api_key=api_key)
    return _client
