"""
Database interactions with tbl_translator.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn


def create_table():
    """
    Create tbl_translator.
    """
    logger.debug("Creating table tbl_translator...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_translator
        (
            id INTEGER PRIMARY KEY,
            surname TEXT,
            forename TEXT NOT NULL,
            UNIQUE(surname, forename)
        ) STRICT
    """
    conn.conn.execute(sql_create_table)


def insert(surname, forename):
    """
    Insert the translator's surname and forename and return the new translator_id.
    The database raises an exception if the translator is already in the database.
    """
    logger.debug(f"surname: '{surname}'")
    logger.debug(f"forename: '{forename}'")
    sql_insert = """
        INSERT INTO tbl_translator
        (
            surname,
            forename
        )
        VALUES (?, ?)
    """
    cur = conn.conn.execute(sql_insert, (surname, forename,))
    translator_id = cur.lastrowid
    cur.close()
    logger.debug(f"New translator_id: {translator_id}")
    return translator_id


def save(surname, forename):
    """
    If the translator exists, select the existing translator_id.
    Otherwise, insert the translator and get the new translator_id.
    Return the translator_id.
    """
    logger.debug(f"surname: '{surname}'")
    logger.debug(f"forename: '{forename}'")
    translator_id = select_id(surname, forename)
    if translator_id is None:
        translator_id = insert(surname, forename)
    logger.debug(f"translator_id: {translator_id}")
    return translator_id


def select_id(surname, forename):
    """
    Select and return the ID for the translator.
    Return None if the translator is not in the database.
    """
    logger.debug(f"surname: '{surname}'")
    logger.debug(f"forename: '{forename}'")
    sql_select_id = """
        SELECT
            tbl_translator.id
        FROM
            tbl_translator
        WHERE
            tbl_translator.surname = ?
            AND tbl_translator.forename = ?
    """
    cur = conn.conn.execute(sql_select_id, (surname, forename,))
    db_row = cur.fetchone()
    cur.close()
    logger.debug(f"Returned row: {db_row}")
    translator_id = None
    if db_row is not None:
        translator_id = db_row[0]
    logger.debug(f"Existing translator_id: {translator_id}")
    return translator_id
