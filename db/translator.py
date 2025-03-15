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
            name TEXT NOT NULL UNIQUE
        )
    """
    conn.conn.execute(sql_create_table)


def insert(translator):
    """
    Insert the translator and return the new translator_id.
    Raises an exception if the translator is already in the database.
    """
    logger.debug(f"translator: '{translator}'")
    sql_insert = """
        INSERT INTO tbl_translator
        (
            name
        )
        VALUES (?)
    """
    cur = conn.conn.execute(sql_insert, (translator,))
    translator_id = cur.lastrowid
    logger.debug(f"New translator_id: {translator_id}")
    return translator_id


def save(translator):
    """
    If the translator exists, select the existing translator_id.
    Otherwise, insert the translator and get the new translator_id.
    Return the translator_id.
    """
    logger.debug(f"translator: '{translator}'")
    translator_id = select_id(translator)
    if translator_id is None:
        translator_id = insert(translator)
    logger.debug(f"translator_id for translator {translator}: {translator_id}")
    return translator_id


def select_id(translator):
    """
    Select and return the ID for the translator.
    Return None if the translator is not in the database.
    """
    logger.debug(f"translator: '{translator}'")
    sql_select_id = """
        SELECT
            tbl_translator.id
        FROM
            tbl_translator
        WHERE
            tbl_translator.name = ?
    """
    cur = conn.conn.execute(sql_select_id, (translator,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for translator '{translator}': {db_row}")
    translator_id = None
    if db_row is not None:
        translator_id = db_row[0]
    logger.debug(f"Existing translator_id: {translator_id}")
    return translator_id
