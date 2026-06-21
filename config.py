import os


class Config:
    SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key")

    db_url = os.environ.get("DATABASE_URL", "")

    # Fix legacy postgres:// prefix (Heroku/Render)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)

    # Fix postgresql:// without driver suffix
    if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    # Fallback to local SQLite so the app still starts without DATABASE_URL
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///mysgym_local.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
