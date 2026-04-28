import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DIGITS_RE = re.compile(r"\D+")


def normalise_phone(phone: str) -> str:
    if phone is None:
        return ""
    return DIGITS_RE.sub("", str(phone))


def is_valid_email(email: str) -> bool:
    if not isinstance(email, str):
        return False
    return bool(EMAIL_RE.match(email.strip()))


def is_valid_phone(normalised: str) -> bool:
    return 10 <= len(normalised) <= 15
