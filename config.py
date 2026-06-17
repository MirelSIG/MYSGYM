import os

class Config:
    SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///mysgym.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Render usa PostgreSQL → psycopg necesita esto
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
