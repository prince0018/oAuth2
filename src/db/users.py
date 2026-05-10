import logging

from src.db.connection import get_connection


logger = logging.getLogger(__name__)


def create_users_table():
    """Create users table if it doesn't exist."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    google_id TEXT UNIQUE,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
                """)
                conn.commit()
    except Exception as e:
        logger.exception("Error creating users table: %s", e)
        raise


def get_or_create_user(email: str, username: str, google_id: str):
    """
    Get existing Google user or create a new one.
    Returns user_id.
    """
    normalized_email = (email or "").strip().lower()
    normalized_google_id = (google_id or "").strip()

    if not normalized_email:
        raise ValueError("Google account did not provide an email address")
    if not normalized_google_id:
        raise ValueError("Google account did not provide a stable user id")

    display_name = (username or "").strip() or normalized_email.split("@")[0]

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, email, username FROM users WHERE google_id = %s;",
                    (normalized_google_id,)
                )
                result = cur.fetchone()

                if result:
                    user_id, current_email, current_username = result
                    if current_email != normalized_email or current_username != display_name:
                        cur.execute(
                            "SELECT id FROM users WHERE email = %s AND id <> %s;",
                            (normalized_email, user_id)
                        )
                        if cur.fetchone():
                            raise ValueError("Email is already linked to another Google account")

                        cur.execute(
                            """
                            UPDATE users
                            SET email = %s, username = %s
                            WHERE id = %s
                            RETURNING id;
                            """,
                            (normalized_email, display_name, user_id)
                        )
                        user_id = cur.fetchone()[0]
                        conn.commit()
                    return user_id

                cur.execute(
                    "SELECT id, google_id FROM users WHERE email = %s;",
                    (normalized_email,)
                )
                existing_email_user = cur.fetchone()

                if existing_email_user:
                    user_id, existing_google_id = existing_email_user
                    if existing_google_id and existing_google_id != normalized_google_id:
                        raise ValueError("Email is already linked to another Google account")

                    cur.execute(
                        """
                        UPDATE users
                        SET google_id = %s, username = %s
                        WHERE id = %s
                        RETURNING id;
                        """,
                        (normalized_google_id, display_name, user_id)
                    )
                    user_id = cur.fetchone()[0]
                    conn.commit()
                    return user_id

                cur.execute(
                    "INSERT INTO users (email, username, google_id) VALUES (%s, %s, %s) RETURNING id;",
                    (normalized_email, display_name, normalized_google_id)
                )
                user_id = cur.fetchone()[0]
                conn.commit()
                return user_id
    except ValueError:
        raise
    except Exception as e:
        logger.exception("Error in get_or_create_user: %s", e)
        return None


def get_user_by_id(user_id: int):
    """Get user details by user_id."""
    if not user_id:
        return None

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, email, username, created_at FROM users WHERE id = %s;",
                    (user_id,)
                )
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "email": row[1],
                    "username": row[2],
                    "created_at": row[3]
                }
    except Exception as e:
        logger.exception("Error getting user by id: %s", e)
        return None


def get_user_by_email(email: str):
    """Get user details by email."""
    if not email:
        return None

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, email, username, created_at FROM users WHERE email = %s;",
                    (email.strip().lower(),)
                )
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "email": row[1],
                    "username": row[2],
                    "created_at": row[3]
                }
    except Exception as e:
        logger.exception("Error getting user by email: %s", e)
        return None
