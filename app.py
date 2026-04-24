import os

from flask import Flask

from infrastructure.database import init_app, init_db
from presentation.routes import app_blueprint


def create_app():
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config["DATABASE"] = os.path.join(flask_app.instance_path, "hobby_meetups.db")
    flask_app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development-secret-key")

    os.makedirs(flask_app.instance_path, exist_ok=True)

    init_app(flask_app)
    flask_app.register_blueprint(app_blueprint)

    with flask_app.app_context():
        init_db()

    return flask_app


app = create_app()


if __name__ == "__main__":
    app.run()
