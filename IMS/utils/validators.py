"""
IMS — Input Validators
Email, phone, DOB, and general field validation utilities.
"""

import re
from datetime import datetime, date


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format. Returns (is_valid, error_message)."""
    if not email or not email.strip():
        return False, "Email is required."
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        return False, "Invalid email format."
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate phone number (10 digits). Returns (is_valid, error_message)."""
    if not phone or not phone.strip():
        return False, "Phone number is required."
    digits = re.sub(r'[^0-9]', '', phone)
    if len(digits) != 10:
        return False, "Phone must be exactly 10 digits."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength. Returns (is_valid, error_message)."""
    if not password:
        return False, "Password is required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


def validate_name(name: str) -> tuple[bool, str]:
    """Validate full name. Returns (is_valid, error_message)."""
    if not name or not name.strip():
        return False, "Name is required."
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters."
    return True, ""


def validate_dob(dob_str: str) -> tuple[bool, str]:
    """
    Validate date of birth string (YYYY-MM-DD format).
    Returns (is_valid, error_message).
    """
    if not dob_str or not dob_str.strip():
        return False, "Date of birth is required."
    try:
        dob = datetime.strptime(dob_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return False, "DOB must be in YYYY-MM-DD format."
    if dob >= date.today():
        return False, "DOB must be in the past."
    return True, ""


def calculate_age(dob: date) -> int:
    """Calculate age from date of birth."""
    today = date.today()
    age = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    return age


def validate_required(value: str, field_name: str) -> tuple[bool, str]:
    """Generic required field validator."""
    if not value or not value.strip():
        return False, f"{field_name} is required."
    return True, ""
