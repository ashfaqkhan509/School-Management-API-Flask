from flask import Flask
from celery_worker import celery_init_app
from school_app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from school_app import tasks  # noqa: F401, noqa: E402


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.from_mapping(
        CELERY=dict(
            broker_url=app.config['CELERY_BROKER_URL'],
            result_backend=app.config['CELERY_RESULT_BACKEND'],
            task_ignore_result=False
        )
    )

    celery_init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from school_app import routes
    app.register_blueprint(routes.bp, url_prefix='/api')

    return app
