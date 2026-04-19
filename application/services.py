from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash


class UserValidationError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class MeetupValidationError(Exception):
    pass


class MeetupNotFoundError(Exception):
    pass


class MeetupPermissionError(Exception):
    pass


class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register_user(self, username, password):
        clean_username = username.strip()
        clean_password = password.strip()

        if not clean_username or not clean_password:
            raise UserValidationError("Username and password are required.")

        if self.user_repository.find_by_username(clean_username) is not None:
            raise UserValidationError("Username already exists.")

        password_hash = generate_password_hash(clean_password, method="pbkdf2:sha256")
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

    def get_user_by_username(self, username):
        return self.user_repository.find_by_username(username.strip())


class MeetupService:
    def __init__(self, meetup_repository):
        self.meetup_repository = meetup_repository

    def list_meetups(self, search_query):
        return self.meetup_repository.list_meetups(search_query)

    def list_meetups_by_user(self, user_id):
        return self.meetup_repository.list_meetups_by_user(user_id)

    def list_join_events_for_meetup(self, meetup_id):
        return self.meetup_repository.list_join_events_for_meetup(meetup_id)

    def get_meetup(self, meetup_id):
        meetup = self.meetup_repository.get_meetup_by_id(meetup_id)
        if meetup is None:
            raise MeetupNotFoundError("Meetup not found.")
        return meetup

    def get_user_profile_stats(self, user_id):
        return self.meetup_repository.get_user_profile_stats(user_id)

    def has_user_joined_meetup(self, meetup_id, user_id):
        return self.meetup_repository.has_user_joined_meetup(meetup_id, user_id)

    def get_categories(self):
        return self.meetup_repository.list_categories()

    def join_meetup(self, meetup_id, user_id, comment):
        clean_comment = comment.strip()
        stored_comment = clean_comment or None
        return self.meetup_repository.create_join_event(meetup_id, user_id, stored_comment)

    def create_meetup(self, user_id, form_data):
        category_ids, title, description, event_time, location = self._validate_meetup_data(form_data)
        return self.meetup_repository.create_meetup(
            user_id,
            category_ids,
            title,
            description,
            event_time,
            location,
        )

    def update_meetup(self, meetup_id, user_id, form_data):
        meetup = self.get_meetup(meetup_id)
        if meetup.user_id != user_id:
            raise MeetupPermissionError("You can edit only your own meetups.")

        category_ids, title, description, event_time, location = self._validate_meetup_data(form_data)
        updated_rows = self.meetup_repository.update_meetup(
            meetup_id,
            user_id,
            category_ids,
            title,
            description,
            event_time,
            location,
        )
        if updated_rows == 0:
            raise MeetupNotFoundError("Meetup not found.")

    def delete_meetup(self, meetup_id, user_id):
        meetup = self.get_meetup(meetup_id)
        if meetup.user_id != user_id:
            raise MeetupPermissionError("You can delete only your own meetups.")

        deleted_rows = self.meetup_repository.delete_meetup(meetup_id, user_id)
        if deleted_rows == 0:
            raise MeetupNotFoundError("Meetup not found.")

    def _validate_meetup_data(self, form_data):
        title = form_data.get("title", "").strip()
        description = form_data.get("description", "").strip()
        event_time = form_data.get("event_time", "").strip()
        location = form_data.get("location", "").strip()
        raw_category_ids = [value.strip() for value in form_data.getlist("category_ids") if value.strip()]

        if not title or not description or not event_time or not location:
            raise MeetupValidationError("All meetup fields are required.")

        categories = self.get_categories()
        if not categories:
            raise MeetupValidationError(
                "No categories are available. Add a category before creating or editing a meetup."
            )

        if not raw_category_ids:
            raise MeetupValidationError("At least one category is required.")

        valid_category_ids = {category.id for category in categories}
        category_ids = []
        for raw_category_id in raw_category_ids:
            try:
                category_id = int(raw_category_id)
            except ValueError as error:
                raise MeetupValidationError("A category is invalid.") from error

            if category_id not in valid_category_ids:
                raise MeetupValidationError("A category is invalid.")

            if category_id not in category_ids:
                category_ids.append(category_id)

        try:
            parsed_event_time = datetime.fromisoformat(event_time)
        except ValueError as error:
            raise MeetupValidationError("Date and time are invalid.") from error

        formatted_event_time = parsed_event_time.strftime("%Y-%m-%d %H:%M:%S")
        return category_ids, title, description, formatted_event_time, location
