"""
Database interactions with tbl_narrator.
"""

import logging

from .. import db

logger = logging.getLogger(__name__)

def create_table():
    """
    Create tbl_narrator.
    """
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_narrator
        (
            id INTEGER PRIMARY KEY,
            surname TEXT NULL,
            forename TEXT NOT NULL,
            UNIQUE(surname, forename)
        ) STRICT
    """
    db.conn.execute(sql_create_table)


def insert(surname, forename):
    """
    Insert the narrator's surname and forename and return the new author_id.
    The database raises an exception if the narrator is already in the database.
    """
    sql_insert = """
        INSERT INTO tbl_narrator
        (
            surname,
            forename
        )
        VALUES (?, ?)
    """
    cur = db.conn.execute(sql_insert, (surname, forename,))
    narrator_id = cur.lastrowid
    cur.close()
    return narrator_id


def save(surname, forename):
    """
    If the narrator exists, select the existing narrator_id.
    Otherwise, insert the narrator and get the new narrator_id.
    Return the narrator_id.
    """
    logger.debug(f"surname: '{surname}'; forename: '{forename}'")
    row = select_id(surname, forename)
    narrator_id = None
    if row is not None:
        logger.debug(f"row: {row}")
        (narrator_id,) = row
    if narrator_id is None:
        narrator_id = insert(surname, forename)
    return narrator_id


def select_id(surname, forename):
    """
    Given the surname and forename of a narrator, return a result set row
    containing the ID of the narrator.

    Return None if the narrator is not in the database.
    """
    sql_select_id = """
        SELECT
            tbl_narrator.id
        FROM
            tbl_narrator
        WHERE
            tbl_narrator.surname = ?
            AND tbl_narrator.forename = ?
    """
    cur = db.conn.execute(sql_select_id, (surname, forename,))
    row = cur.fetchone()
    cur.close()
    return row


# def select_narrators_for_book(book_id):
#     """
#     Given a book's ID, return result set rows containing the narrators of
#     the book.
#
#     Return an empty list if narrators are not found.
#
#     Deprecated.
#     """
#     sql_select_narrators_for_book = """
#         SELECT
#             tbl_narrator.id,
#             tbl_narrator.surname,
#             tbl_narrator.forename
#         FROM
#             tbl_book_narrator
#             INNER JOIN tbl_narrator
#                 ON tbl_book_narrator.narrator_id = tbl_narrator.id
#         WHERE
#             tbl_book_narrator.book_id = ?
#     """
#     cur = db.conn.execute(sql_select_narrators_for_book, (book_id,))
#     rows = cur.fetchall()
#     cur.close()
#     return rows


def select_ids_for_book(book_id):
    """
    Given a book's ID, return result set rows containing the IDs of the
    narrators of the book.

    Return an empty list if no narrators are found.
    """
    sql_select_ids_for_book = """
        SELECT
            tbl_narrator.id
        FROM
            tbl_book_narrator
            INNER JOIN tbl_narrator
                ON tbl_book_narrator.narrator_id = tbl_narrator.id
        WHERE
            tbl_book_narrator.book_id = ?
    """
    cur = db.conn.execute(sql_select_ids_for_book, (book_id,))
    rows = cur.fetchall()
    cur.close()
    return rows


def select_narrator(narrator_id):
    """
    Given a narrator's ID, return a result set row containing the narrator's
    attributes.

    Return None if the narrator's ID is not in the database.
    """
    sql_select_narrator = """
        SELECT
            tbl_narrator.id,
            tbl_narrator.surname,
            tbl_narrator.forename
        FROM
            tbl_narrator
        WHERE
            tbl_narrator.id = ?
    """
    cur = db.conn.execute(sql_select_narrator, (narrator_id,))
    row = cur.fetchone()
    cur.close()
    return row
