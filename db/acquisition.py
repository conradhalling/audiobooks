"""
Database interactions with tbl_book_acquisition.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn

def create_table():
    """
    Create tbl_acquisition.
    """
    logger.debug("Creating table tbl_acquisition...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_acquisition
        (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            acquisition_type_id INTEGER NOT NULL,
            acquisition_date TEXT NOT NULL,
            discontinued TEXT NULL,
            audible_credits INTEGER NULL,
            price_in_cents INTEGER NULL,
            FOREIGN KEY (user_id) REFERENCES tbl_user(id),
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (vendor_id) REFERENCES tbl_vendor(id),
            FOREIGN KEY (acquisition_type_id) REFERENCES tbl_acquisition_type(id),
            UNIQUE (user_id, book_id, vendor_id)
        ) STRICT
    """
    conn.conn.execute(sql_create_table)


def insert(user_id, book_id, vendor_id, acquisition_type_id, acquisition_date,
        discontinued, audible_credits=None, price_in_cents=None):
    """
    Insert the acquisition and return the new acquisition_id.
    Raises an exception if the acquisition is already in the database.
    """
    logger.debug(f"user_id: {user_id}")
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"vendor_id: {vendor_id}")
    logger.debug(f"acquisition_type_id: {acquisition_type_id}")
    logger.debug(f"acquisition_date: {acquisition_date}")
    logger.debug(f"discontinued: {discontinued}")
    logger.debug(f"audible_credits: {audible_credits}")
    logger.debug(f"price_in_cents: {price_in_cents}")
    sql_insert = """
    INSERT INTO
        tbl_acquisition
        (
            user_id,
            book_id,
            vendor_id,
            acquisition_type_id,
            acquisition_date,
            discontinued,
            audible_credits,
            price_in_cents
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.conn.execute(
        sql_insert,
        (
            user_id,
            book_id, 
            vendor_id, 
            acquisition_type_id, 
            acquisition_date,
            discontinued,
            audible_credits, 
            price_in_cents,
        )
    )
    acquisition_id = cur.lastrowid
    logger.debug(f"New acquisition_id: {acquisition_id}")
    return acquisition_id


def save(user_id, book_id, vendor_id, acquisition_type_id, acquisition_date,
        discontinued, audible_credits=None, price_in_cents=None):
    """
    If the acquisition exists, select the existing book_acquisition_id.
    Otherwise, insert the book acquisition and get the new book_acquisition_id.
    Return the book_acquisition_id.
    """
    logger.debug(f"user_id: {user_id}")
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"vendor_id: {vendor_id}")
    logger.debug(f"acquisition_type_id: {acquisition_type_id}")
    logger.debug(f"acquisition_date: '{acquisition_date}'")
    logger.debug(f"discontinued: {discontinued}")
    logger.debug(f"audible_credits: {audible_credits}")
    logger.debug(f"price_in_cents: {price_in_cents}")
    acquisition_id = select_id(user_id, book_id, vendor_id)
    if acquisition_id is None:
        acquisition_id = insert(
            user_id, book_id, vendor_id, acquisition_type_id, acquisition_date,
            discontinued, audible_credits, price_in_cents)
    logger.debug(f"acquisition_id: {acquisition_id}")
    return acquisition_id


def select_id(user_id, book_id, vendor_id):
    """
    Select and return the ID for the acquisition.
    Return None if the acquisition is not in the database.
    """
    sql_select_id = """
        SELECT
            tbl_acquisition.id
        FROM
            tbl_acquisition
        WHERE
            tbl_acquisition.user_id = ?
            AND tbl_acquisition.book_id = ?
            AND tbl_acquisition.vendor_id = ?
    """
    logger.debug(f"user_id: {user_id}")
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"vendor_id: {vendor_id}")
    cur = conn.conn.execute(sql_select_id, (user_id, book_id, vendor_id,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row: {db_row}")
    acquisition_id = None
    if db_row is not None:
        acquisition_id = db_row[0]
    logger.debug(f"Existing acquisition_id: {acquisition_id}")
    return acquisition_id
