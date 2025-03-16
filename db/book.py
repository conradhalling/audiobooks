"""
Database interactions with tbl_book.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn

def create_table():
    """
    Create tbl_book.
    """
    logger.debug("Creating table tbl_book...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_book
        (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL UNIQUE,
            book_pub_date TEXT,
            audio_pub_date TEXT,
            hours INTEGER NOT NULL,
            minutes INTEGER NOT NULL,
            discontinued TEXT
        )"""
    conn.conn.execute(sql_create_table)


def insert(title, book_pub_date, audio_pub_date, hours, minutes, discontinued):
    """
    Insert the book and return the new book_id.
    Raises an exception if the book is already in the database.
    """
    logger.debug(f"title: '{title}'")
    logger.debug(f"book_pub_date: '{book_pub_date}'")
    logger.debug(f"audio_pub_date: '{audio_pub_date}'")
    logger.debug(f"hours: {hours}")
    logger.debug(f"minutes: {minutes}")
    logger.debug(f"discontinued: '{discontinued}'")
    sql_insert = """
        INSERT INTO tbl_book
        (
            title,
            book_pub_date,
            audio_pub_date,
            hours,
            minutes,
            discontinued
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cur = conn.conn.execute(sql_insert, (title, book_pub_date, audio_pub_date, hours, minutes, discontinued,))
    book_id = cur.lastrowid
    logger.debug(f"New book_id: {book_id}")
    return book_id


def save(title, book_pub_date, audio_pub_date, hours, minutes, discontinued):
    """
    If the book exists, select the existing book_id.
    Otherwise, insert the book and get the new book_id.
    Return the book_id.
    """
    logger.debug(f"title: '{title}'")
    logger.debug(f"book_pub_date: '{book_pub_date}'")
    logger.debug(f"audio_pub_date: '{audio_pub_date}'")
    logger.debug(f"hours: {hours}")
    logger.debug(f"minutes: {minutes}")
    logger.debug(f"discontinued: '{discontinued}'")
    book_id = select_id(title)
    if book_id is None:
        book_id = insert(title, book_pub_date, audio_pub_date, hours, minutes, discontinued)
    logger.debug(f"book_id for title {title}: {book_id}")
    return book_id


def select_id(title):
    """
    Select and return the ID for the book.
    Return None if the book is not in the database.
    """
    logger.debug(f"book title: '{title}'")
    sql_select_id = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
        WHERE
            tbl_book.title = ?
    """
    cur = conn.conn.execute(sql_select_id, (title,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for title '{title}': {db_row}")
    book_id = None
    if db_row is not None:
        book_id = db_row[0]
    logger.debug(f"Existing book_id: {book_id}")
    return book_id
