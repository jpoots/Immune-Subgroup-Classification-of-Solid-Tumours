from app import celery, create_app

"""
activates the celery worker
"""

app = create_app()
app.app_context().push()


# code taken directly from https://blog.miguelgrinberg.com/post/celery-and-the-flask-application-factory-pattern
