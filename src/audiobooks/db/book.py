"""
Database interactions with tbl_book.
"""

import logging
logger = logging.getLogger(__name__)

from .. import db

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
            minutes INTEGER NOT NULL
        ) STRICT
    """
    db.conn.execute(sql_create_table)


def insert(title, book_pub_date, audio_pub_date, hours, minutes):
    """
    Insert the book and return the new book ID.

    The database's unique constraint raises an exception if the book is already
    in the database.
    """
    logger.debug(f"title: '{title}'")
    logger.debug(f"book_pub_date: '{book_pub_date}'")
    logger.debug(f"audio_pub_date: '{audio_pub_date}'")
    logger.debug(f"hours: {hours}")
    logger.debug(f"minutes: {minutes}")
    sql_insert = """
        INSERT INTO tbl_book
        (
            title,
            book_pub_date,
            audio_pub_date,
            hours,
            minutes
        )
        VALUES (?, ?, ?, ?, ?)
    """
    cur = db.conn.execute(
        sql_insert, (title, book_pub_date, audio_pub_date, hours, minutes))
    book_id = cur.lastrowid
    logger.debug(f"New book_id: {book_id}")
    return book_id


def save(title, book_pub_date, audio_pub_date, hours, minutes):
    """
    If the book exists, select and return the existing book ID.

    Otherwise, insert the book and return the new book ID.
    """
    logger.debug(f"title: '{title}'")
    logger.debug(f"book_pub_date: '{book_pub_date}'")
    logger.debug(f"audio_pub_date: '{audio_pub_date}'")
    logger.debug(f"hours: {hours}")
    logger.debug(f"minutes: {minutes}")
    row = select_id(title)
    book_id = None
    if row is not None:
        book_id = row[0]
    logger.debug(f"Existing book_id: {book_id}")
    if book_id is None:
        book_id = insert(title, book_pub_date, audio_pub_date, hours, minutes)
    logger.debug(f"book_id for title '{title}': {book_id}")
    return book_id


def select_book(book_id):
    """
    Given a book's ID, select and return a result set row containing the book's
    attributes.

    Return None if the book's ID isn't in the database.
    """
    sql_select_book = """
        SELECT
            tbl_book.id,
            tbl_book.title,
            tbl_book.book_pub_date,
            tbl_book.audio_pub_date,
            tbl_book.hours,
            tbl_book.minutes
        FROM
            tbl_book
        WHERE
            tbl_book.id = ?
    """
    cur = db.conn.execute(sql_select_book, (book_id,))
    row = cur.fetchone()
    cur.close()
    return row


# def select_books_for_author(conn, author_id):
#     """
#     Deprecated.
#     """
#     sql_select_books_for_author = """
#         SELECT
#             tbl_book.title,
#             tbl_book.book_pub_date,
#             tbl_book.audio_pub_date,
#             tbl_book.hours,
#             tbl_book.minutes,
#             tbl_book.id
#         FROM
#             tbl_book
#             INNER JOIN tbl_book_author
#                 ON tbl_book.id = tbl_book_author.book_id
#         WHERE
#             tbl_book_author.author_id = ?
#     """
#     cur = db.conn.execute(sql_select_books_for_author, (author_id,))
#     rows = cur.fetchall()
#     cur.close()
#     return rows


def select_id(title):
    """
    Given a book's title, select and return a result set row containing the ID
    for the book.

    Return None if the book's title is not in the database.
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
    cur = db.conn.execute(sql_select_id, (title,))
    row = cur.fetchone()
    logger.debug(f"Returned row for title '{title}': {row}")
    return row


def select_ids():
    """
    Return result set rows containing all book IDs.

    The result set is an empty list if no book IDs are found.
    """
    sql_select_ids = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
    """
    cur = db.conn.execute(sql_select_ids)
    rows = cur.fetchall()
    cur.close()
    return rows


def select_ids_for_author(author_id):
    """
    Return result set rows containing book IDs for an author.

    The result set is an empty list if no book IDs are found.
    """
    sql_select_ids_for_author = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
            INNER JOIN tbl_book_author
                ON tbl_book.id = tbl_book_author.book_id
        WHERE
            tbl_book_author.author_id = ?
    """
    cur = db.conn.execute(sql_select_ids_for_author, (author_id,))
    rows = cur.fetchall()
    cur.close()
    return rows


def select_ids_for_narrator(narrator_id):
    """
    Return result set rows containing book IDs for a narrator.

    The result set is an empty list if no book IDs are found.
    """
    sql_select_ids_for_narrator = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
            INNER JOIN tbl_book_narrator
                ON tbl_book.id = tbl_book_narrator.book_id
        WHERE
            tbl_book_narrator.narrator_id = ?
    """
    cur = db.conn.execute(sql_select_ids_for_narrator, (narrator_id,))
    rows = cur.fetchall()
    cur.close()
    return rows


def select_ids_for_translator(translator_id):
    """
    Return result set rows containing book IDs for a translator.

    The result set is an empty list if no book IDs are found.
    """
    sql_select_ids_for_translator = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
            INNER JOIN tbl_book_translator
                ON tbl_book.id = tbl_book_translator.book_id
        WHERE
            tbl_book_translator.translator_id = ?
    """
    cur = db.conn.execute(sql_select_ids_for_translator, (translator_id,))
    rows = cur.fetchall()
    cur.close()
    return rows
