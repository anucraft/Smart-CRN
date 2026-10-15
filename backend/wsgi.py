"""Entry point used by `flask` CLI and by gunicorn (`gunicorn wsgi:app`)."""
from app import create_app

app = create_app()
