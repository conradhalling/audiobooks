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
            surname TEXT NULL,
            forename TEXT NOT NULL,
            UNIQUE(surname, forename)
        ) STRICT
    """
    conn.conn.execute(sql_create_table)


def insert(surname, forename):
    """
    Insert the author's surname and forename and return the new author_id.
    The database raises an exception if the author is already in the database.
    """
    logger.debug(f"surname: '{surname}'")
    logger.debug(f"forename: '{forename}'")
    if surname == "":
        surname = None
    if forename == "":
        raise ValueError("The forename must not be empty")
    sql_insert = """
        INSERT INTO tbl_author
        (
            surname,
            forename
        )
        VALUES (?, ?)
    """
    cur = conn.conn.execute(sql_insert, (surname, forename,))
    author_id = cur.lastrowid
    cur.close()
    logger.debug(f"New author_id: {author_id}")
    return author_id


def save(surname, forename):
    """
    If the author exists, select the existing author_id.
    Otherwise, insert the author and get the new author_id.
    Return the author_id.
    """
    logger.debug(f"surname: '{surname}'")
    logger.debug(f"forename: '{forename}'")
    author_id = select_id(surname, forename)
    if author_id is None:
        author_id = insert(surname, forename)
    logger.debug(f"author_id: {author_id}")
    return author_id


def select_id(surname, forename):
    """
    Select and return the ID for the author.
    Return None if the author is not in the database.
    """
    logger.debug(f"surname: '{surname}'")
    logger.debug(f"forename: '{forename}'")
    cur = conn.conn.cursor()
    if surname is None:
        sql_select_id = """
            SELECT
                tbl_author.id
            FROM
                tbl_author
            WHERE
                tbl_author.forename = ?
                AND tbl_author.surname IS NULL
        """
        cur.execute(sql_select_id, (forename,))
    else:
        sql_select_id = """
            SELECT
                tbl_author.id
            FROM
                tbl_author
            WHERE
                tbl_author.surname = ?
                AND tbl_author.forename = ?
        """
        cur.execute(sql_select_id, (surname, forename))
    db_row = cur.fetchone()
    cur.close()
    logger.debug(f"Returned row: {db_row}")
    author_id = None
    if db_row is not None:
        author_id = db_row[0]
    logger.debug(f"Existing author_id: {author_id}")
    return author_id
