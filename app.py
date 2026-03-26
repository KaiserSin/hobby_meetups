import os

from flask import Flask

from infrastructure.database import init_app, init_db
from presentation.routes import auth_blueprint


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["DATABASE"] = os.path.join(app.instance_path, "hobby_meetups.db")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development-secret-key")

    os.makedirs(app.instance_path, exist_ok=True)

    init_app(app)
    app.register_blueprint(auth_blueprint)

    with app.app_context():
        init_db()

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
