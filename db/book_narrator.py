"""
Database interactions with tbl_book_narrator.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn

def create_table():
    """
    Create table tbl_book_narrator.
    """
    logger.debug("Creating tbl_book_narrator...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_book_narrator
        (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            narrator_id INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (narrator_id) REFERENCES tbl_narrator(id)
        ) strict
    """
    conn.conn.execute(sql_create_table)

def insert(book_id, narrator_id):
    """
    Insert the book narrator and return the new book_narrator_id.
    """
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"narrator_id: {narrator_id}")
    sql_insert = """
        INSERT INTO tbl_book_narrator
        (
            book_id,
            narrator_id
        )
        VALUES (?, ?)
    """
    cur = conn.conn.execute(sql_insert, (book_id, narrator_id,))
    book_narrator_id = cur.lastrowid
    logger.debug(f"New book_narrator_id: {book_narrator_id}")
    return book_narrator_id


def save(book_id, narrator_id):
    """
    If the book narrator exists, select the existing book_narrator_id.
    Otherwise, insert the book narrator and get the new book_narrator_id.
    Return the book_narrator_id.
    """
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"narratorid: {narrator_id}")
    book_narrator_id = select_id(book_id, narrator_id)
    if book_narrator_id is None:
        book_narrator_id = insert(book_id, narrator_id)
    logger.debug(f"book_narrator_id: {book_narrator_id}")
    return book_narrator_id


def select_id(book_id, narrator_id):
    """
    Select and return the ID for the book narrator.
    Return None if the book narrator is not in the database.
    """
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"narratorid: {narrator_id}")
    sql_select_id = """
        SELECT
            tbl_book_narrator.id
        FROM
            tbl_book_narrator
        WHERE
            tbl_book_narrator.book_id = ?
            AND tbl_book_narrator.narrator_id = ?
    """
    cur = conn.conn.execute(sql_select_id, (book_id, narrator_id,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row {db_row}")
    book_narrator_id = None
    if db_row is not None:
        book_narrator_id = db_row[0]
    logger.debug(f"Existing book_narrator_id: {book_narrator_id}")
    return book_narrator_id
