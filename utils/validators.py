import re


def validate_mobile(mobile: str) -> bool:
    digits = re.sub(r"\D", "", mobile)
    return len(digits) >= 10


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email)) if email else True


def validate_age(age) -> bool:
    try:
        return 0 <= int(age) <= 150
    except (ValueError, TypeError):
        return False


def sanitize_filename(filename: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
