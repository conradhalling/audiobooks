"""
Database interactions with tbl_author.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn


def create_table():
    """
    Create tbl_author.
    """
    logger.debug("Creating table tbl_author...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_author
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        ) strict
    """
    conn.conn.execute(sql_create_table)


def insert(author):
    """
    Insert the author and return the new author_id.
    Raises an exception if the author is already in the database.
    """
    logger.debug(f"author: '{author}'")
    sql_insert = """
        INSERT INTO tbl_author
        (
            name
        )
        VALUES (?)
    """
    cur = conn.conn.execute(sql_insert, (author,))
    author_id = cur.lastrowid
    logger.debug(f"New author_id: {author_id}")
    return author_id


def save(author):
    """
    If the author exists, select the existing author_id.
    Otherwise, insert the author and get the new author_id.
    Return the author_id.
    """
    logger.debug(f"author: '{author}'")
    author_id = select_id(author)
    if author_id is None:
        author_id = insert(author)
    logger.debug(f"author_id for author {author}: {author_id}")
    return author_id


def select_id(author):
    """
    Select and return the ID for the author.
    Return None if the author is not in the database.
    """
    logger.debug(f"author: '{author}'")
    sql_select_id = """
        SELECT
            tbl_author.id
        FROM
            tbl_author
        WHERE
            tbl_author.name = ?
    """
    cur = conn.conn.execute(sql_select_id, (author,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for author '{author}': {db_row}")
    author_id = None
    if db_row is not None:
        author_id = db_row[0]
    logger.debug(f"Existing author_id: {author_id}")
    return author_id
