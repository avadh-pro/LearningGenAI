"""FastAPI entrypoint."""

import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status

from app.config import Settings, get_settings
from app.llm_service import (
    LLMRateLimitError,
    LLMService,
    LLMServiceError,
    LLMUnavailableError,
)
from app.logging_config import configure_logging
from app.schemas import GenerateRequest, HealthResponse, SupportResponse
from app.validation import InputValidationError, validate_and_normalize_message

logger = logging.getLogger(__name__)


def get_llm_service(request: Request) -> LLMService:
    service = request.app.state.llm_service
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured",
        )
    return service


def create_app(
    settings: Settings | None = None,
    llm_service: LLMService | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    created_service = llm_service
    if created_service is None and settings.openai_is_configured:
        created_service = LLMService(
            api_key=settings.openai_api_key.get_secret_value(),  # type: ignore[union-attr]
            model=settings.openai_model,
            timeout_seconds=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.settings = settings
        application.state.llm_service = created_service
        logger.info(
            "application_started",
            extra={"model": settings.openai_model},
        )
        yield
        if created_service is not None and hasattr(created_service, "close"):
            await created_service.close()

    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Baseline production deployment using the OpenAI Responses API.",
        lifespan=lifespan,
    )

    @application.middleware("http")
    async def request_logging(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            logger.info(
                "http_request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )

    @application.get("/health", response_model=HealthResponse, tags=["operations"])
    async def health() -> HealthResponse:
        return HealthResponse(
            status="healthy",
            environment=settings.app_env,
            model=settings.openai_model,
            openai_configured=created_service is not None,
        )

    @application.post(
        "/generate",
        response_model=SupportResponse,
        status_code=status.HTTP_200_OK,
        tags=["generation"],
    )
    async def generate(
        payload: GenerateRequest,
        service: Annotated[LLMService, Depends(get_llm_service)],
    ) -> SupportResponse:
        try:
            message = validate_and_normalize_message(
                payload.message,
                max_chars=settings.max_input_chars,
            )
        except InputValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc

        try:
            return await service.generate(message)
        except LLMRateLimitError as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        except LLMUnavailableError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except LLMServiceError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return application


app = create_app()
