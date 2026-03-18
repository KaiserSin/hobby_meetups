import os

from flask import Flask

from infrastructure.database import init_app, init_db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["DATABASE"] = os.path.join(app.instance_path, "hobby_meetups.db")

    os.makedirs(app.instance_path, exist_ok=True)

    init_app(app)

    with app.app_context():
        init_db()

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
