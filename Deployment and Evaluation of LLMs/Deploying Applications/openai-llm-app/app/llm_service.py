"""OpenAI Responses API integration."""

import logging
import time

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.schemas import SupportResponse

logger = logging.getLogger(__name__)


class LLMServiceError(RuntimeError):
    """Base error safe to translate into an HTTP response."""


class LLMRateLimitError(LLMServiceError):
    pass


class LLMUnavailableError(LLMServiceError):
    pass


class LLMService:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_retries: int,
    ) -> None:
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=max_retries,
        )

    async def generate(self, message: str) -> SupportResponse:
        """Classify a message and return a schema-validated response."""

        started = time.perf_counter()
        try:
            response = await self.client.responses.parse(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=build_user_prompt(message),
                text_format=SupportResponse,
            )
        except RateLimitError as exc:
            raise LLMRateLimitError("OpenAI rate limit reached") from exc
        except (APIConnectionError, APITimeoutError) as exc:
            raise LLMUnavailableError("OpenAI is temporarily unavailable") from exc
        except APIError as exc:
            logger.exception("openai_api_error")
            raise LLMServiceError("OpenAI request failed") from exc

        parsed = response.output_parsed
        if parsed is None:
            raise LLMServiceError("OpenAI did not return a structured response")

        usage = getattr(response, "usage", None)
        logger.info(
            "openai_request_completed",
            extra={
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                "model": self.model,
                "openai_response_id": getattr(response, "id", None),
                "input_tokens": getattr(usage, "input_tokens", None),
                "output_tokens": getattr(usage, "output_tokens", None),
            },
        )
        return parsed

    async def close(self) -> None:
        await self.client.close()
