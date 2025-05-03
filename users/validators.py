# users/validators.py

def validate_password(password: str) -> str:
    """
    Validates a password for complexity requirements.
    Raises ValueError if the password does not meet the criteria.
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit.")
    if not any(char in "!@#$%^&*()_+-=.,'" for char in password):
        raise ValueError("Password must contain at least one special character.")
    return password