import hashlib
import hmac
import secrets

def generate_csrf_token():
    return secrets.token_hex(16)

PASSWORD_METHOD = "pbkdf2:sha256"
PASSWORD_ITERATIONS = 1_000_000

def generate_password_hash(password):
    """Return a salted PBKDF2 password hash."""
    salt = secrets.token_hex(8)
    password_hash = _pbkdf2_hash(password, salt, PASSWORD_ITERATIONS)
    return f"{PASSWORD_METHOD}:{PASSWORD_ITERATIONS}${salt}${password_hash}"

def check_password_hash(stored_hash, password):
    """Check a password against a PBKDF2 hash."""
    try:
        method, salt, expected_hash = stored_hash.split("$", 2)
        algorithm, iterations = _parse_password_method(method)
    except (AttributeError, TypeError, ValueError):
        return False

    password_hash = _pbkdf2_hash(password, salt, iterations, algorithm)
    return hmac.compare_digest(password_hash, expected_hash)

def _parse_password_method(method):
    method_parts = method.split(":")
    if len(method_parts) == 2:
        method_name, algorithm = method_parts
        iterations = PASSWORD_ITERATIONS
    elif len(method_parts) == 3:
        method_name, algorithm, raw_iterations = method_parts
        iterations = int(raw_iterations)
    else:
        raise ValueError("Unsupported password hash method.")

    if method_name != "pbkdf2":
        raise ValueError("Unsupported password hash method.")

    return algorithm, iterations

def _pbkdf2_hash(password, salt, iterations, algorithm="sha256"):
    return hashlib.pbkdf2_hmac(
        algorithm,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
