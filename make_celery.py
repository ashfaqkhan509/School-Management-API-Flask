from school_app import create_app


flask_app = create_app()
celery_app = flask_app.extensions['celery']

import school_app.tasks
