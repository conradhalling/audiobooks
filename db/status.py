"""
Database interactions with tbl_status.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn


def create_table():
    """
    Create tbl_status.
    """
    logger.debug("Creating table tbl_status...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_status
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        ) STRICT
    """
    conn.conn.execute(sql_create_table)


def insert(status):
    """
    Insert the status and return the status_id.
    Raises an exception if the status is already in the table.
    """
    logger.debug(f"status: '{status}'")
    sql_insert = """
        INSERT INTO tbl_status
        (
            name
        )
        VALUES (?)
    """
    cur = conn.conn.execute(sql_insert, (status,))
    status_id = cur.lastrowid
    logger.debug(f"New status_id: {status_id}")
    return status_id


def save(status):
    """
    If the status exists, select the existing status_id.
    Otherwise, insert the status and get the new status_id.
    Return the status_id.
    """
    logger.debug(f"status: '{status}'")
    status_id = select_id(status)
    if status_id is None:
        status_id = insert(status)
    logger.debug(f"status_id for status '{status}': {status_id}")
    return status_id


def select_id(status):
    """
    Select and return the ID for the status.
    Return None if the status is not in the database.
    """
    logger.debug(f"status: '{status}'")
    sql_select_id = """
        SELECT
            tbl_status.id
        FROM
            tbl_status
        WHERE
            tbl_status.name = ?
    """
    cur = conn.conn.execute(sql_select_id, (status,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for status '{status}': {db_row}")
    status_id = None
    if db_row is not None:
        status_id = db_row[0]
    logger.debug(f"Existing status_id: {status_id}")
    return status_id
