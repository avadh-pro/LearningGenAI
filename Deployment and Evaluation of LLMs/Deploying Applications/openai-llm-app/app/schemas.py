"""Pydantic request and structured-response schemas."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Category(str, Enum):
    ORDER = "ORDER"
    PAYMENT = "PAYMENT"
    ACCOUNT = "ACCOUNT"
    PRODUCT = "PRODUCT"
    OTHER = "OTHER"


class Intent(str, Enum):
    DELIVERY_DELAY = "DELIVERY_DELAY"
    ORDER_STATUS = "ORDER_STATUS"
    CANCEL_ORDER = "CANCEL_ORDER"
    REFUND_REQUEST = "REFUND_REQUEST"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    ACCOUNT_ACCESS = "ACCOUNT_ACCESS"
    PRODUCT_QUESTION = "PRODUCT_QUESTION"
    OTHER = "OTHER"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        min_length=1,
        max_length=4000,
        description="The customer support message to classify and answer.",
        examples=["My order was due yesterday. Where is it?"],
    )


class SupportResponse(BaseModel):
    """Schema enforced by both OpenAI Structured Outputs and FastAPI."""

    model_config = ConfigDict(extra="forbid")

    category: Category
    intent: Intent
    priority: Priority
    reply: str = Field(min_length=1, max_length=1000)


class HealthResponse(BaseModel):
    status: str
    environment: str
    model: str
    openai_configured: bool
