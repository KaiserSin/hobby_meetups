from flask import Blueprint, redirect, render_template, request, session, url_for

from application.user_service import (
    AuthenticationError,
    UserService,
    UserValidationError,
)
from infrastructure.repositories import UserRepository


auth_blueprint = Blueprint("auth", __name__)
user_service = UserService(UserRepository())


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
            session["user_id"] = user["id"]
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
