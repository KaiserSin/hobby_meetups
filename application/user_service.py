from werkzeug.security import check_password_hash, generate_password_hash


class UserValidationError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register_user(self, username, password):
        clean_username = username.strip()
        clean_password = password.strip()

        if not clean_username or not clean_password:
            raise UserValidationError("Username and password are required.")

        existing_user = self.user_repository.find_by_username(clean_username)
        if existing_user is not None:
            raise UserValidationError("Username already exists.")

        password_hash = generate_password_hash(
            clean_password,
            method="pbkdf2:sha256",
        )
        user_id = self.user_repository.save_user(clean_username, password_hash)
        return self.user_repository.get_user_by_id(user_id)

    def authenticate_user(self, username, password):
        clean_username = username.strip()
        clean_password = password.strip()

        if not clean_username or not clean_password:
            raise UserValidationError("Username and password are required.")

        user = self.user_repository.find_by_username(clean_username)
        if user is None or not check_password_hash(user.password_hash, clean_password):
            raise AuthenticationError("Invalid username or password.")

        return user
