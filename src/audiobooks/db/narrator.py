"""
Database interactions with tbl_narrator.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn


def create_table():
    """
    Create tbl_narrator.
    """
    logger.debug("Creating table tbl_narrator...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_narrator
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
    Insert the narrator's surname and forename and return the new author_id.
    The database raises an exception if the narrator is already in the database.
    """
    logger.debug(f"surname: '{surname}'")
    logger.debug(f"forename: '{forename}'")
    sql_insert = """
        INSERT INTO tbl_narrator
        (
            surname,
            forename
        )
        VALUES (?, ?)
    """
    cur = conn.conn.execute(sql_insert, (surname, forename,))
    narrator_id = cur.lastrowid
    cur.close()
    logger.debug(f"New narrator_id: {narrator_id}")
    return narrator_id


def save(surname, forename):
    """
    If the narrator exists, select the existing narrator_id.
    Otherwise, insert the narrator and get the new narrator_id.
    Return the narrator_id.
    """
    logger.debug(f"surname: '{surname}'")
    logger.debug(f"forename: '{forename}'")
    narrator_id = select_id(surname, forename)
    if narrator_id is None:
        narrator_id = insert(surname, forename)
    logger.debug(f"narrator_id: {narrator_id}")
    return narrator_id


def select_id(surname, forename):
    """
    Select and return the ID for the narrator.
    Return None if the narrator is not in the database.
    """
    logger.debug(f"surname: '{surname}'")
    logger.debug(f"forename: '{forename}'")
    sql_select_id = """
        SELECT
            tbl_narrator.id
        FROM
            tbl_narrator
        WHERE
            tbl_narrator.surname = ?
            AND tbl_narrator.forename = ?
    """
    cur = conn.conn.execute(sql_select_id, (surname, forename,))
    db_row = cur.fetchone()
    cur.close()
    logger.debug(f"Returned row: {db_row}")
    narrator_id = None
    if db_row is not None:
        narrator_id = db_row[0]
    logger.debug(f"Existing narrator_id: {narrator_id}")
    return narrator_id
