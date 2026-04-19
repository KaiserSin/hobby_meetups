from functools import wraps
import secrets

from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from application.security import generate_csrf_token
from application.services import (
    AuthenticationError,
    MeetupNotFoundError,
    MeetupPermissionError,
    MeetupService,
    MeetupValidationError,
    UserService,
    UserValidationError,
)
from infrastructure.repositories import MeetupRepository, UserRepository


app_blueprint = Blueprint("app", __name__)
user_service = UserService(UserRepository())
meetup_service = MeetupService(MeetupRepository())


@app_blueprint.app_context_processor
def inject_user_state():
    return {
        "current_user_id": _current_user_id(),
        "csrf_token": _ensure_csrf_token(),
    }


def _current_user_id():
    return session.get("user_id")


def _ensure_csrf_token():
    csrf_token = session.get("csrf_token")
    if csrf_token is None:
        csrf_token = generate_csrf_token()
        session["csrf_token"] = csrf_token
    return csrf_token


def _rotate_csrf_token():
    session["csrf_token"] = generate_csrf_token()


def _validate_csrf_or_403():
    session_token = session.get("csrf_token")
    form_token = request.form.get("csrf_token")
    if not session_token or not form_token or not secrets.compare_digest(form_token, session_token):
        abort(403)


def _get_meetup_or_404(meetup_id):
    try:
        return meetup_service.get_meetup(meetup_id)
    except MeetupNotFoundError:
        abort(404)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if _current_user_id() is None:
            return redirect(url_for("app.login"))
        return view(*args, **kwargs)

    return wrapped_view


@app_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        _validate_csrf_or_403()
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        try:
            user_service.register_user(username, password)
            return redirect(url_for("app.login", registered="1"))
        except UserValidationError as error:
            return render_template("register.html", error_message=str(error))

    return render_template("register.html")


@app_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        _validate_csrf_or_403()
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        try:
            user = user_service.authenticate_user(username, password)
            session["user_id"] = user.id
            _rotate_csrf_token()
            return redirect(url_for("app.index", status="logged_in"))
        except (UserValidationError, AuthenticationError) as error:
            return render_template("login.html", error_message=str(error))

    status_message = None

    if request.args.get("registered") == "1":
        status_message = "Registration successful. Please log in."
    elif request.args.get("logged_out") == "1":
        status_message = "You have been logged out."
    elif _current_user_id() is not None:
        status_message = "You are already logged in."

    return render_template("login.html", status_message=status_message)


@app_blueprint.route("/logout", methods=["POST"])
def logout():
    _validate_csrf_or_403()
    session.pop("user_id", None)
    return redirect(url_for("app.index", status="logged_out"))


@app_blueprint.route("/")
def index():
    search_query = request.args.get("search_query", "").strip()
    status = request.args.get("status")
    status_message = None

    if status == "logged_in":
        status_message = "Login successful."
    elif status == "logged_out":
        status_message = "You have been logged out."

    meetups = meetup_service.list_meetups(search_query)
    return render_template(
        "index.html",
        meetups=meetups,
        search_query=search_query,
        status_message=status_message,
    )


@app_blueprint.route("/user/<username>")
def user_profile(username):
    profile_user = user_service.get_user_by_username(username)
    if profile_user is None:
        abort(404)

    organized_count, joined_count = meetup_service.get_user_profile_stats(profile_user.id)
    meetups = meetup_service.list_meetups_by_user(profile_user.id)
    is_owner = _current_user_id() == profile_user.id

    return render_template(
        "profile.html",
        profile_user=profile_user,
        organized_count=organized_count,
        joined_count=joined_count,
        meetups=meetups,
        is_owner=is_owner,
    )


@app_blueprint.route("/meetups/<int:meetup_id>")
def meetup_detail(meetup_id):
    meetup = _get_meetup_or_404(meetup_id)
    current_user_id = _current_user_id()
    is_owner = current_user_id == meetup.user_id
    join_events = meetup_service.list_join_events_for_meetup(meetup_id)
    has_joined = current_user_id is not None and any(
        join_event["user_id"] == current_user_id for join_event in join_events
    )

    status_message = None
    error_message = None
    status = request.args.get("status")
    if status == "joined":
        status_message = "You joined this meetup."
    elif status == "already_joined":
        error_message = "You have already joined this meetup."
    elif status == "join_not_allowed":
        error_message = "You cannot join your own meetup."

    return render_template(
        "meetup_detail.html",
        meetup=meetup,
        is_owner=is_owner,
        join_events=join_events,
        can_join=current_user_id is not None and not is_owner and not has_joined,
        has_joined=has_joined,
        show_joined_note=has_joined and status not in {"joined", "already_joined"},
        status_message=status_message,
        error_message=error_message,
    )


@app_blueprint.route("/meetups/create", methods=["GET", "POST"])
@login_required
def create_meetup():
    categories = meetup_service.get_categories()
    if not categories:
        return render_template(
            "create_meetup.html",
            categories=[],
            error_message="No categories are available. Add a category before creating a meetup.",
        )

    if request.method == "POST":
        _validate_csrf_or_403()
        try:
            meetup_id = meetup_service.create_meetup(_current_user_id(), request.form)
            return redirect(url_for("app.meetup_detail", meetup_id=meetup_id))
        except MeetupValidationError as error:
            return render_template(
                "create_meetup.html",
                categories=categories,
                error_message=str(error),
            )

    return render_template(
        "create_meetup.html",
        categories=categories,
    )


@app_blueprint.route("/meetups/<int:meetup_id>/edit", methods=["GET", "POST"])
@login_required
def edit_meetup(meetup_id):
    meetup = _get_meetup_or_404(meetup_id)
    if meetup.user_id != _current_user_id():
        abort(403)

    categories = meetup_service.get_categories()
    if not categories:
        return render_template(
            "edit_meetup.html",
            meetup=meetup,
            categories=[],
            error_message="No categories are available. Add a category before editing a meetup.",
        )

    if request.method == "POST":
        _validate_csrf_or_403()
        try:
            meetup_service.update_meetup(meetup_id, _current_user_id(), request.form)
            return redirect(url_for("app.meetup_detail", meetup_id=meetup_id))
        except MeetupValidationError as error:
            return render_template(
                "edit_meetup.html",
                meetup=meetup,
                categories=categories,
                error_message=str(error),
            )
        except MeetupPermissionError:
            abort(403)
        except MeetupNotFoundError:
            abort(404)

    return render_template(
        "edit_meetup.html",
        meetup=meetup,
        categories=categories,
    )


@app_blueprint.route("/meetups/<int:meetup_id>/delete", methods=["GET", "POST"])
@login_required
def delete_meetup(meetup_id):
    meetup = _get_meetup_or_404(meetup_id)
    if meetup.user_id != _current_user_id():
        abort(403)

    if request.method == "POST":
        _validate_csrf_or_403()
        try:
            meetup_service.delete_meetup(meetup_id, _current_user_id())
        except MeetupPermissionError:
            abort(403)
        except MeetupNotFoundError:
            abort(404)

        return redirect(url_for("app.index"))

    return render_template("delete_meetup.html", meetup=meetup)


@app_blueprint.route("/meetups/<int:meetup_id>/join", methods=["POST"])
def join_meetup(meetup_id):
    _validate_csrf_or_403()
    meetup = _get_meetup_or_404(meetup_id)
    user_id = _current_user_id()
    if user_id is None:
        return redirect(url_for("app.login"))

    if meetup.user_id == user_id:
        return redirect(url_for("app.meetup_detail", meetup_id=meetup_id, status="join_not_allowed"))

    if meetup_service.has_user_joined_meetup(meetup_id, user_id):
        return redirect(url_for("app.meetup_detail", meetup_id=meetup_id, status="already_joined"))

    comment = request.form.get("comment", "")
    meetup_service.join_meetup(meetup_id, user_id, comment)

    return redirect(
        url_for(
            "app.meetup_detail",
            meetup_id=meetup_id,
            status="joined",
        )
    )
