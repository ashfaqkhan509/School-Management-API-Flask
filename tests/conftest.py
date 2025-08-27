from school_app import create_app, db
import pytest
from school_app.config import TestConfig


@pytest.fixture(scope='function')
def app():
    """
    Pytest fixture to create a Flask application instance for testing.

    - Uses the TestConfig class for database and app configuration.
    - Initializes the database schema before tests run.
    - Provides the application context to tests.
    - Tears down the database schema after all tests complete.

    Yields:
        Flask: A configured Flask application instance for testing.
    """
    app = create_app()
    app.config.from_object(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Pytest fixture to provide a test client for the Flask application.

    - Allows sending simulated HTTP requests to the app without running a server.
    - Useful for testing routes and APIs.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        FlaskClient: A test client instance for sending requests.
    """
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def celery_eager(app):
    """
    Run Celery tasks synchronously in tests.
    """
    celery = app.extensions["celery"]
    celery.conf.update(task_always_eager=True)
    yield celery
    celery.conf.update(task_always_eager=False)
