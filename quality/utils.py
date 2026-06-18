import re

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(value):
    if value is None:
        return False
    if not isinstance(value, str):
        return False
    return bool(EMAIL_PATTERN.match(value.strip()))
