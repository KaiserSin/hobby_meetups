import secrets

try:
    from werkzeug.security import check_password_hash as werkzeug_check_password_hash
    from werkzeug.security import generate_password_hash as werkzeug_generate_password_hash
except ImportError:
    werkzeug_check_password_hash = None
    werkzeug_generate_password_hash = None

def generate_csrf_token():
    return secrets.token_hex(16)

def generate_password_hash(password):
    if werkzeug_generate_password_hash is None:
        raise RuntimeError("Werkzeug is required for password hashing.")

    return werkzeug_generate_password_hash(password, method="pbkdf2:sha256")

def check_password_hash(stored_hash, password):
    if werkzeug_check_password_hash is None:
        raise RuntimeError("Werkzeug is required for password checking.")

    return werkzeug_check_password_hash(stored_hash, password)
