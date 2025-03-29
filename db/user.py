"""
Database interactions with tbl_user.
"""

import logging
logger = logging.getLogger(__name__)

import argon2

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
        ) STRICT
    """
    conn.conn.execute(sql_create_table)


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


def select_password_hash(username):
    """
    For the given username, select the password_hash value from tbl_user.
    Raise an exception if the username is not found.
    """
    logger.debug(f"username: '{username}'")
    sql_select_password_hash = """
        SELECT
            tbl_user.password_hash
        FROM
            tbl_user
        WHERE
            tbl_user.username = ?
    """
    cur = conn.conn.execute(sql_select_password_hash, (username,))
    db_row = cur.fetchone()
    # logger.debug(f"Returned row for username '{username}': {db_row}")
    if db_row is None:
        raise ValueError(f"Username '{username}' not found")
    password_hash = db_row[0]
    return password_hash


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
    logger.debug(f"Existing user_id: {user_id}")
    return user_id


def verify_username_password(username, password):
    """
    Raise an exception if username is not in the table.
    Raise an exception if the password wasn't verified.
    Hide the earlier exception so the user won't which of the username
    or password was not verified.
    """
    error = False
    try:
        ph = argon2.PasswordHasher()
        password_hash = select_password_hash(username)
        ph.verify(password_hash, password)
    except Exception:
        error = True
    if error:
        raise ValueError("Can't verify username and/or password")
    return
