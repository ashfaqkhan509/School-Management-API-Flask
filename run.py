from school_app.models import (
    Student,
    Course,
    Enrollment,
    Assignment,
    Lesson,
    Result
)
from school_app import db, create_app
import os


app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    Provides shell context for Flask CLI.

    This allows direct access to the database instance (db) and
    model classes (Customer, Order, Product, OrderItem)
    when running `flask shell`.

    Returns:
        dict: A dictionary mapping names to objects for use in the shell.
    """
    return {
        'db': db,
        'Student': Student,
        'Course': Course,
        'Enrollment': Enrollment,
        'Lesson': Lesson,
        'Assignement': Assignment,
        'Result': Result
    }


if __name__ == '__main__':
    """
    Entry point for running the Flask application.

    Reads the port number from the environment variable `PORT`
    (default: 5000), enables debug mode, and listens on all network interfaces.
    """
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
