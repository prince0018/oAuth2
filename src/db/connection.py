import psycopg2

from src.config import get_settings


def get_connection():
    """Get PostgreSQL database connection."""
    settings = get_settings()
    connection_kwargs = {
        "dbname": settings.db_name,
        "user": settings.db_user,
        "host": settings.db_host,
        "port": settings.db_port,
        "connect_timeout": 5,
    }
    if settings.db_password:
        connection_kwargs["password"] = settings.db_password

    return psycopg2.connect(
        **connection_kwargs
    )
