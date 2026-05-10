from src.db.connection import get_connection


def create_users_table():
    """Create users table if it doesn't exist."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT,
                    google_id TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                conn.commit()
        print("✅ Users table created/verified")
    except Exception as e:
        print(f"❌ Error creating users table: {e}")


def get_or_create_user(email: str, username: str, google_id: str):
    """
    Get existing user or create new one.
    Returns user_id.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check if user exists by email
                cur.execute(
                    "SELECT id FROM users WHERE email = %s;",
                    (email,)
                )
                result = cur.fetchone()
                
                if result:
                    # User exists, return id
                    return result[0]
                
                # User doesn't exist, create new one
                cur.execute(
                    "INSERT INTO users (email, username, google_id) VALUES (%s, %s, %s) RETURNING id;",
                    (email, username, google_id)
                )
                user_id = cur.fetchone()[0]
                conn.commit()
                return user_id
    except Exception as e:
        print(f"❌ Error in get_or_create_user: {e}")
        return None


def get_user_by_id(user_id: int):
    """Get user details by user_id."""
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
        print(f"❌ Error getting user by id: {e}")
        return None


def get_user_by_email(email: str):
    """Get user details by email."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, email, username, created_at FROM users WHERE email = %s;",
                    (email,)
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
        print(f"❌ Error getting user by email: {e}")
        return None
