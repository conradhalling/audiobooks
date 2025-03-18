"""
Database interactions with tbl_book_translator.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn

def create_table():
    """
    Create table tbl_book_translator.
    """
    logger.debug("Creating tbl_book_translator...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_book_translator
        (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            translator_id INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (translator_id) REFERENCES tbl_translator(id)
        ) strict
    """
    conn.conn.execute(sql_create_table)

def insert(book_id, translator_id):
    """
    Insert the book translator and return the new book_translator_id.
    """
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"translator_id: {translator_id}")
    sql_insert = """
        INSERT INTO
            tbl_book_translator
            (
                book_id,
                translator_id
            )
            VALUES (?, ?)
    """
    cur = conn.conn.execute(sql_insert, (book_id, translator_id,))
    book_translator_id = cur.lastrowid
    logger.debug(f"New book_translator_id: {book_translator_id}")
    return book_translator_id


def save(book_id, translator_id):
    """
    If the book translator exists, select the existing book_translator_id.
    Otherwise, insert the book translator and get the new book_translator_id.
    Return the book_translator_id.
    """
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"translator_id: {translator_id}")
    book_translator_id = select_id(book_id, translator_id)
    if book_translator_id is None:
        book_translator_id = insert(book_id, translator_id)
    logger.debug(f"book_translator_id: {book_translator_id}")
    return book_translator_id


def select_id(book_id, translator_id):
    """
    Select and return the ID for the book translator.
    Return None if the book translator is not in the database.
    """
    sql_select_id = """
        SELECT
            tbl_book_translator.id
        FROM
            tbl_book_translator
        WHERE
            tbl_book_translator.book_id = ?
            AND tbl_book_translator.translator_id = ?
    """
    cur = conn.conn.execute(sql_select_id, (book_id, translator_id,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row {db_row}")
    book_translator_id = None
    if db_row is not None:
        book_translator_id = db_row[0]
    logger.debug(f"Existing book_translator_id: {book_translator_id}")
    return book_translator_id
