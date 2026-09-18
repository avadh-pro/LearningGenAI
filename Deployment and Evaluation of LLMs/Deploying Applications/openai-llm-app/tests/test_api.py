from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.schemas import Category, Intent, Priority, SupportResponse


def test_health_without_api_key() -> None:
    settings = Settings(_env_file=None, openai_api_key=None)
    application = create_app(settings=settings)

    with TestClient(application) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "environment": "development",
        "model": "gpt-4.1-mini",
        "openai_configured": False,
    }
    assert response.headers["X-Request-ID"]


def test_generate_returns_structured_response() -> None:
    service = AsyncMock()
    service.generate.return_value = SupportResponse(
        category=Category.ORDER,
        intent=Intent.DELIVERY_DELAY,
        priority=Priority.MEDIUM,
        reply="I’m sorry your order has been delayed. Please share your order number.",
    )
    settings = Settings(_env_file=None, openai_api_key=None)
    application = create_app(settings=settings, llm_service=service)

    with TestClient(application) as client:
        response = client.post(
            "/generate",
            json={"message": "  My delivery is late.  "},
        )

    assert response.status_code == 200
    assert response.json()["intent"] == "DELIVERY_DELAY"
    service.generate.assert_awaited_once_with("My delivery is late.")


def test_generate_rejects_blank_input() -> None:
    service = AsyncMock()
    settings = Settings(_env_file=None, openai_api_key=None)
    application = create_app(settings=settings, llm_service=service)

    with TestClient(application) as client:
        response = client.post("/generate", json={"message": "   "})

    assert response.status_code == 422
    assert "non-whitespace" in response.json()["detail"]
    service.generate.assert_not_awaited()


def test_generate_requires_api_key() -> None:
    settings = Settings(_env_file=None, openai_api_key=None)
    application = create_app(settings=settings)

    with TestClient(application) as client:
        response = client.post("/generate", json={"message": "Where is my order?"})

    assert response.status_code == 503
    assert response.json()["detail"] == "OPENAI_API_KEY is not configured"


def test_generate_rejects_extra_fields() -> None:
    service = AsyncMock()
    settings = Settings(_env_file=None, openai_api_key=None)
    application = create_app(settings=settings, llm_service=service)

    with TestClient(application) as client:
        response = client.post(
            "/generate",
            json={"message": "Where is my order?", "admin": True},
        )

    assert response.status_code == 422
    service.generate.assert_not_awaited()
