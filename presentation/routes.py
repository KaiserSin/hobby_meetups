from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from application.meetup_service import (
    MeetupNotFoundError,
    MeetupPermissionError,
    MeetupService,
    MeetupValidationError,
)
from application.user_service import (
    AuthenticationError,
    UserService,
    UserValidationError,
)
from infrastructure.repositories import MeetupRepository, UserRepository


auth_blueprint = Blueprint("auth", __name__)
meetups_blueprint = Blueprint("meetups", __name__)
user_service = UserService(UserRepository())
meetup_service = MeetupService(MeetupRepository())


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        try:
            user_service.register_user(username, password)
            return redirect(url_for("auth.login", registered="1"))
        except UserValidationError as error:
            return render_template("register.html", error_message=str(error))

    return render_template("register.html", error_message=None)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        try:
            user = user_service.authenticate_user(username, password)
            session["user_id"] = user.id
            return redirect(url_for("auth.login", logged_in="1"))
        except UserValidationError as error:
            return render_template(
                "login.html",
                error_message=str(error),
                status_message=None,
            )
        except AuthenticationError as error:
            return render_template(
                "login.html",
                error_message=str(error),
                status_message=None,
            )

    status_message = None

    if request.args.get("registered") == "1":
        status_message = "Registration successful. Please log in."
    elif request.args.get("logged_out") == "1":
        status_message = "You have been logged out."
    elif "user_id" in session:
        status_message = "You are already logged in."

    return render_template(
        "login.html",
        error_message=None,
        status_message=status_message,
    )


@auth_blueprint.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("auth.login", logged_out="1"))


@meetups_blueprint.route("/")
def index():
    search_query = request.args.get("search_query", "").strip()
    meetups = meetup_service.list_meetups(search_query)
    return render_template("index.html", meetups=meetups, search_query=search_query)


@meetups_blueprint.route("/meetups/<int:meetup_id>")
def meetup_detail(meetup_id):
    try:
        meetup = meetup_service.get_meetup(meetup_id)
    except MeetupNotFoundError:
        abort(404)

    status_message = None
    if request.args.get("status") == "join_unavailable":
        status_message = "This feature is not part of the current deadline."

    return render_template(
        "meetup_detail.html",
        meetup=meetup,
        status_message=status_message,
        error_message=None,
    )


@meetups_blueprint.route("/meetups/create", methods=["GET", "POST"])
def create_meetup():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.login"))

    categories = meetup_service.get_categories()
    if not categories:
        return render_template(
            "create_meetup.html",
            categories=[],
            error_message="No categories are available. Add a category before creating a meetup.",
        )

    if request.method == "POST":
        try:
            meetup_id = meetup_service.create_meetup(user_id, request.form)
            return redirect(url_for("meetups.meetup_detail", meetup_id=meetup_id))
        except MeetupValidationError as error:
            return render_template(
                "create_meetup.html",
                categories=categories,
                error_message=str(error),
            )

    return render_template(
        "create_meetup.html",
        categories=categories,
        error_message=None,
    )


@meetups_blueprint.route("/meetups/<int:meetup_id>/edit", methods=["GET", "POST"])
def edit_meetup(meetup_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.login"))

    try:
        meetup = meetup_service.get_meetup(meetup_id)
    except MeetupNotFoundError:
        abort(404)

    if meetup.user_id != user_id:
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
        try:
            meetup_service.update_meetup(meetup_id, user_id, request.form)
            return redirect(url_for("meetups.meetup_detail", meetup_id=meetup_id))
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
        error_message=None,
    )


@meetups_blueprint.route("/meetups/<int:meetup_id>/delete", methods=["POST"])
def delete_meetup(meetup_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.login"))

    try:
        meetup_service.delete_meetup(meetup_id, user_id)
    except MeetupPermissionError:
        abort(403)
    except MeetupNotFoundError:
        abort(404)

    return redirect(url_for("meetups.index"))


@meetups_blueprint.route("/meetups/<int:meetup_id>/join", methods=["POST"])
def join_meetup(meetup_id):
    try:
        meetup_service.get_meetup(meetup_id)
    except MeetupNotFoundError:
        abort(404)

    return redirect(
        url_for(
            "meetups.meetup_detail",
            meetup_id=meetup_id,
            status="join_unavailable",
        )
    )
