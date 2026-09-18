"""Input normalization performed before prompt construction."""

import re


class InputValidationError(ValueError):
    """Raised when a message is unsafe or unusable as model input."""


_DISALLOWED_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def validate_and_normalize_message(message: str, max_chars: int) -> str:
    """Trim input and reject empty, oversized, or binary-like content."""

    normalized = message.strip()
    if not normalized:
        raise InputValidationError("message must contain non-whitespace characters")
    if len(normalized) > max_chars:
        raise InputValidationError(f"message must be at most {max_chars} characters")
    if _DISALLOWED_CONTROL_CHARS.search(normalized):
        raise InputValidationError("message contains unsupported control characters")
    return normalized
