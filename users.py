import sqlite3
from global_config import DATABASE, pwd_context


def create_user(form_data, canvas_id, canvas_name):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # if user_exists(username, cursor):
        #     return False
        # else:
        hashed_password = pwd_context.hash(form_data.password)
        cursor.execute(
            """
            INSERT INTO users (username, hashed_password, url, bid, canvas_id, canvas_name) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                form_data.username,
                hashed_password,
                form_data.url,
                form_data.bid,
                canvas_id,
                canvas_name,
            ),
        )
        conn.commit()
        return True


def get_hashed_password(username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT hashed_password FROM users WHERE username = ?
        """,
            (username, ),
        )
        result = cursor.fetchone()
        return result[0] if result else None


def user_exists(username, cursor=None):
    if cursor is None:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            return user_exists(username, cursor)
    else:
        cursor.execute(
            """
            SELECT id FROM users WHERE username = ?
        """,
            (username, ),
        )
        return cursor.fetchone() is not None


def same_user(url, canvas_id, cursor=None):
    if cursor is None:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            return same_user(url, canvas_id, cursor)
    else:
        cursor.execute(
            # Every user of a Canvas LMS has a unique canvas_id
            """
                SELECT id FROM users WHERE url = ? AND canvas_id = ?
        """,
            (url, canvas_id),
        )
        return cursor.fetchone() is not None
