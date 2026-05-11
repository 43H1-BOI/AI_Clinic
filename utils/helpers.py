import os
import uuid
from datetime import datetime


def generate_unique_filename(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1] if "." in original_filename else ""
    return f"{uuid.uuid4().hex}{ext}"


def get_today_date() -> str:
    return datetime.now().strftime("%d-%m-%Y")


def get_current_datetime() -> str:
    return datetime.now().strftime("%d-%m-%Y %H:%M")


def format_date_for_display(date_str: str) -> str:
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        return dt.strftime("%d %b %Y")
    except ValueError:
        return date_str
