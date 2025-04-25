"""
Database interactions with tbl_book_author.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn

def create_table():
    """
    Create table tbl_book_author.
    """
    logger.debug("Creating tbl_book_author...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_book_author
        (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (author_id) REFERENCES tbl_author(id)
        ) STRICT
    """
    conn.conn.execute(sql_create_table)

def insert(book_id, author_id):
    """
    Insert the book author and return the new book_author_id.
    """
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"author_id: {author_id}")
    sql_insert = """
        INSERT INTO
            tbl_book_author
            (
                book_id,
                author_id
            )
            VALUES (?, ?)
    """
    cur = conn.conn.execute(sql_insert, (book_id, author_id,))
    book_author_id = cur.lastrowid
    logger.debug(f"New book_author_id: {book_author_id}")
    return book_author_id


def save(book_id, author_id):
    """
    If the book author exists, select the existing book_author_id.
    Otherwise, insert the book author and get the new book_author_id.
    Return the book_author_id.
    """
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"author_id: {author_id}")
    book_author_id = select_id(book_id, author_id)
    if book_author_id is None:
        book_author_id = insert(book_id, author_id)
    logger.debug(f"book_author_id: {book_author_id}")
    return book_author_id


def select_id(book_id, author_id):
    """
    Select and return the ID for the book author.
    Return None if the book author is not in the database.
    """
    sql_select_id = """
        SELECT
            tbl_book_author.id
        FROM
            tbl_book_author
        WHERE
            tbl_book_author.book_id = ?
            AND tbl_book_author.author_id = ?
    """
    cur = conn.conn.execute(sql_select_id, (book_id, author_id,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for book_id {book_id} author_id {author_id}: {db_row}")
    book_author_id = None
    if db_row is not None:
        book_author_id = db_row[0]
    logger.debug(f"Existing book_author_id: {book_author_id}")
    return book_author_id
