from typing import Any

from openai import (
    APIConnectionError,
    APIError as OpenAIAPIError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from .constants import DEFAULT_MODEL, RETRY_MAX_ATTEMPTS, RETRY_MAX_SECONDS, RETRY_MIN_SECONDS
from .exceptions import APIError


def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, APIConnectionError):
        return True
    if isinstance(exc, OpenAIAPIError):
        status = getattr(exc, "status_code", None)
        return status is not None and status >= 500
    return False


class OpenAITranscriptionClient:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    @retry(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(min=RETRY_MIN_SECONDS, max=RETRY_MAX_SECONDS),
        reraise=True,
    )
    def transcribe_file(self, audio_file: str) -> str:
        try:
            with open(audio_file, "rb") as handle:
                result: Any = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=handle,
                    response_format="text",
                )
        except (AuthenticationError, BadRequestError) as exc:
            raise APIError("Authentication or request error.") from exc
        except Exception as exc:
            if _is_retryable(exc):
                raise
            raise APIError("Failed to transcribe audio.") from exc

        if isinstance(result, str):
            return result
        if hasattr(result, "text"):
            return result.text
        return str(result)
