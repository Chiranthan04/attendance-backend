import re

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple:
    """Validate password strength. Returns (is_valid, error_message)"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, ""

def validate_required_fields(data: dict, required_fields: list) -> tuple:
    """Check if all required fields are present. Returns (is_valid, missing_fields)"""
    missing = [field for field in required_fields if field not in data or not data[field]]
    return len(missing) == 0, missing
