"""
Database interactions with tbl_acquisition_type.
"""

import logging

from . import conn

logger = logging.getLogger(__name__)

def create_table():
    """
    Create tbl_acquisition_type.
    """
    logger.debug("Creating tbl_acqusition_type...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_acquisition_type
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        ) strict
    """
    conn.conn.execute(sql_create_table)
    acquisition_types = ['vendor credit', 'charge', 'no charge']
    for acquisition_type in acquisition_types:
        save(acquisition_type)


def insert(acquisition_type):
    logger.debug(f"acquisition_type: '{acquisition_type}'")
    sql_insert = """
        INSERT INTO tbl_acquisition_type
        (
            name
        )
        VALUES (?)
    """
    cur = conn.conn.execute(sql_insert, (acquisition_type,))
    acquisition_type_id = cur.lastrowid
    logger.debug(f"New acquisition_type_id: {acquisition_type_id}")
    return acquisition_type_id


def save(acquisition_type):
    """
    If the acquisition_type exists, select the existing acquisition_type_id.
    Otherwise, insert the acquisition_type and get the new acquisition_type_id.
    Return the acquisiton_type_id.
    """
    logger.debug(f"acquisition_type: '{acquisition_type}'")
    acquisition_type_id = select_id(acquisition_type)
    if acquisition_type_id is None:
        acquisition_type_id = insert(acquisition_type)
    logger.debug(f"acquisition_type_id for acquisition_type '{acquisition_type}': {acquisition_type_id}")
    return acquisition_type_id


def select_id(acquisition_type):
    logger.debug(f"acquisition_type: '{acquisition_type}'")
    sql_select_id = """
        SELECT
            tbl_acquisition_type.id
        FROM
            tbl_acquisition_type
        WHERE
            tbl_acquisition_type.name = ?
    """
    cur = conn.conn.execute(sql_select_id, (acquisition_type,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for acquisiton_type '{acquisition_type}': {db_row}")
    acquisition_type_id = None
    if db_row is not None:
        acquisition_type_id = db_row[0]
    logger.debug(f"Existing acquistion_type_id: {acquisition_type_id}")
    return acquisition_type_id
