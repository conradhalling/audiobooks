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
            name TEXT NOT NULL UNIQUE
        ) strict
    """
    conn.conn.execute(sql_create_table)


def insert(narrator):
    """
    Insert the narrator and return the narrator_id.
    Raises an exception if the narrator is already in the database.
    """
    logger.debug(f"narrator: '{narrator}'")
    sql_insert = """
        INSERT INTO tbl_narrator
        (
            name
        )
        VALUES (?)
    """
    cur = conn.conn.execute(sql_insert, (narrator,))
    narrator_id = cur.lastrowid
    logger.debug(f"New narrator_id: {narrator_id}")
    return narrator_id


def save(narrator):
    """
    If the narrator exists, select the existing narrator_id.
    Otherwise, insert the narrator and get the new narrator_id.
    Return the narrator_id.
    """
    logger.debug(f"narrator: '{narrator}'")
    narrator_id = select_id(narrator)
    if narrator_id is None:
        narrator_id = insert(narrator)
    logger.debug(f"narrator_id for narrator '{narrator}': {narrator_id}")
    return narrator_id


def select_id(narrator):
    """
    Select and return the ID for the narrator.
    Return None if the narrator is not in the database.
    """
    logger.debug(f"narrator: '{narrator}'")
    sql_select_id = """
        SELECT
            tbl_narrator.id
        FROM
            tbl_narrator
        WHERE
            tbl_narrator.name = ?
    """
    cur = conn.conn.execute(sql_select_id, (narrator,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for narrator '{narrator}': {db_row}")
    narrator_id = None
    if db_row is not None:
        narrator_id = db_row[0]
    logger.debug(f"Existing narrator_id: {narrator_id}")
    return narrator_id
