"""
Database interactions with tbl_user.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn


def create_table():
    """
    Create tbl_user.
    """
    logger.debug("Creating table tbl_user...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_user
        (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    """
    conn.conn.execute(sql_create_table)
    insert('halto', 'conrad.halling@icloud.com', 'xxxxxxxxxx')


def insert(username, email, password_hash):
    """
    Insert the user and return the new user_id.
    Raises an exception if the user is already in the database.
    """
    logger.debug(f"username: '{username}'")
    logger.debug(f"email: '{email}'")
    logger.debug(f"password_hash: '{password_hash}'")
    sql_insert = """
        INSERT INTO tbl_user
        (
            username,
            email,
            password_hash
        )
        VALUES (?, ?, ?)
    """
    cur = conn.conn.execute(sql_insert, (username, email, password_hash,))
    user_id = cur.lastrowid
    logger.debug(f"New user_id: {user_id}")
    return user_id


def select_user_id(username):
    """
    Select and return the user_id for the username.
    Return None if the user is not in the database.
    """
    logger.debug(f"username: '{username}'")
    sql_select_user = """
        SELECT
            tbl_user.id
        FROM
            tbl_user
        WHERE
            tbl_user.username = ?
    """
    cur = conn.conn.execute(sql_select_user, (username,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for username '{username}': {db_row}")
    user_id = None
    if db_row is not None:
        user_id = db_row[0]
    logger.debug(f"Exiting user_id: {user_id}")
    return user_id
