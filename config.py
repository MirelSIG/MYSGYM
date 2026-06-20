import os

class Config:
    SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key")

    db_url = os.environ.get("DATABASE_URL", "")

    # Fix Render/Heroku prefix
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)

    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
