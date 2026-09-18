import pytest

from app.validation import InputValidationError, validate_and_normalize_message


def test_normalizes_surrounding_whitespace() -> None:
    assert validate_and_normalize_message("  hello\n", 100) == "hello"


def test_rejects_control_characters() -> None:
    with pytest.raises(InputValidationError, match="control"):
        validate_and_normalize_message("hello\x00world", 100)


def test_rejects_runtime_length_limit() -> None:
    with pytest.raises(InputValidationError, match="at most"):
        validate_and_normalize_message("abcdef", 5)
