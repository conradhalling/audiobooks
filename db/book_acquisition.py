"""
Database interactions with tbl_book_acquisition.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn

def create_table():
    """
    Create tbl_book_acquisition.
    """
    logger.debug("Creating table tbl_book_acquisition...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_book_acquisition
        (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            acquisition_type_id INTEGER NOT NULL,
            acquisition_date TEXT NOT NULL,
            audible_credits INTEGER NULL,
            price_in_cents INTEGER NULL,
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (vendor_id) REFERENCES tbl_vendor(id),
            FOREIGN KEY (acquisition_type_id) REFERENCES tbl_acquisition_type(id),
            UNIQUE (book_id, vendor_id)
        )
    """
    conn.conn.execute(sql_create_table)


def insert(book_id, vendor_id, acquisition_type_id, acquisition_date,
        audible_credits, price_in_cents):
    """
    Insert the book acquisition and return the new book_acquisition_id.
    Raises an exception if the book acquisition is already in the database.
    """
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"vendor_id: {vendor_id}")
    logger.debug(f"acquisition_type_id: {acquisition_type_id}")
    logger.debug(f"acquisition_date: {acquisition_date}")
    logger.debug(f"audible_credits: {audible_credits}")
    logger.debug(f"price_in_cents: {price_in_cents}")
    sql_insert = """
    INSERT INTO
        tbl_book_acquisition
        (
            book_id,
            vendor_id,
            acquisition_type_id,
            acquisition_date,
            audible_credits,
            price_in_cents
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cur = conn.conn.execute(
        sql_insert,
        (
            book_id, 
            vendor_id, 
            acquisition_type_id, 
            acquisition_date,
            audible_credits, 
            price_in_cents,
        )
    )
    book_acquisition_id = cur.lastrowid
    logger.debug(f"New book_acquisition_id: {book_acquisition_id}")
    return book_acquisition_id


def save(book_id, vendor_id, acquisition_type_id, acquisition_date,
        audible_credits, price_in_cents):
    """
    If the book acquisition exists, select the existing book_acquisition_id.
    Otherwise, insert the book acquisition and get the new book_acquisition_id.
    Return the book_acquisition_id.
    """
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"vendor_id: {vendor_id}")
    logger.debug(f"acquisition_type_id: {acquisition_type_id}")
    logger.debug(f"acquisition_date: '{acquisition_date}'")
    logger.debug(f"audible_credits: {audible_credits}")
    logger.debug(f"price_in_cents: {price_in_cents}")
    book_acquisition_id = select_id(book_id, vendor_id)
    if book_acquisition_id is None:
        book_acquisition_id = insert(
            book_id, vendor_id, acquisition_type_id, acquisition_date,
            audible_credits, price_in_cents)
    logger.debug(f"book_acquisition_id: {book_acquisition_id}")
    return book_acquisition_id


def select_id(book_id, vendor_id):
    """
    Select and return the ID for the book acquisition.
    Return None if the book acquisition is not in the database.
    """
    sql_select_id = """
        SELECT
            tbl_book_acquisition.id
        FROM
            tbl_book_acquisition
        WHERE
            tbl_book_acquisition.book_id = ?
            AND tbl_book_acquisition.vendor_id = ?
    """
    cur = conn.conn.execute(sql_select_id, (book_id, vendor_id,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for book_id {book_id} vendor_id {vendor_id}: {db_row}")
    book_acquisition_id = None
    if db_row is not None:
        book_acquisition_id = db_row[0]
    logger.debug(f"Existing book_acquisition_id: {book_acquisition_id}")
    return book_acquisition_id
