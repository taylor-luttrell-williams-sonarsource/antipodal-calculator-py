"""
WSGI entry point for the Antipodal Calculator API.

Run locally with:
    python wsgi.py

Or behind a WSGI server with:
    gunicorn wsgi:app
"""

from antipodal.webapp import create_app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
