"""
Database interactions with tbl_note.

The user will update the note when the user finishes the audiobook.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn


def create_table():
    """
    Create tbl_note.
    """
    logger.debug("Creating table tbl_note...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_note (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            reread TEXT,
            status_id INTEGER NOT NULL,
            finish_date TEXT,
            rating_id INTEGER,
            comments TEXT,
            FOREIGN KEY (user_id) REFERENCES tbl_user(id),
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (status_id) REFERENCES tbl_status(id),
            FOREIGN KEY (rating_id) REFERENCES tbl_rating(id)
        )
    """
    conn.conn.execute(sql_create_table)


def insert(user_id, book_id, reread, status_id, finish_date, rating_id, comments):
    """
    Insert the note and return the new note_id.
    """
    logger.debug(f"user_id: {user_id}")
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"reread: '{reread}'")
    logger.debug(f"status_id: {status_id}")
    logger.debug(f"finish_date: '{finish_date}'")
    logger.debug(f"rating_id: {rating_id}")
    logger.debug(f"comments: '{comments}'")
    sql_insert = """
        INSERT INTO tbl_note
        (
            user_id,
            book_id,
            reread,
            status_id,
            finish_date,
            rating_id,
            comments
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.conn.execute(
        sql_insert,
        (user_id, book_id, reread, status_id, finish_date, rating_id, comments))
    note_id = cur.lastrowid
    logger.debug(f"New note_id: {note_id}")
    return note_id


def save(user_id, book_id, reread, status_id, finish_date, rating_id, comments):
    """
    If the note exists, select the existing note_id.
    Otherwise, insert the note and get the new note_id.
    Return the note_id.
    """
    logger.debug(f"user_id: {user_id}")
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"reread: '{reread}'")
    logger.debug(f"status_id: {status_id}")
    logger.debug(f"finish_date: '{finish_date}'")
    logger.debug(f"rating_id: {rating_id}")
    logger.debug(f"comments: '{comments}'")
    note_id = select_id(user_id, book_id, reread, status_id, finish_date, rating_id, comments)
    if note_id is None:
        note_id = insert(user_id, book_id, reread, status_id, finish_date, rating_id, comments)
    logger.debug(f"note_id: {note_id}")
    return note_id


def select_id(user_id, book_id, reread, status_id, finish_date, rating_id, comments):
    """
    Select and return the ID for the note.
    Return None if the note is not in the database.
    This is to prevent inserting the same data into the database more than
    once.
    """
    logger.debug(f"user_id: {user_id}")
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"reread: '{reread}'")
    logger.debug(f"status: {status_id}")
    logger.debug(f"finish_date: '{finish_date}'")
    logger.debug(f"rating_id: {rating_id}")
    logger.debug(f"comments: '{comments}'")
    # Build the query string to allow for NULL values.
    # This is inconvenient but is necessary for the query to work correctly.
    sql_select_id = f"""
        SELECT
            tbl_note.id
        FROM
            tbl_note
        WHERE
            tbl_note.user_id = ?
            AND tbl_note.book_id = ?
            AND tbl_note.reread {'IS NULL' if reread is None else '= ?'}
            AND tbl_note.status_id {'IS NULL' if status_id is None else '= ?'}
            AND tbl_note.finish_date {'IS NULL' if finish_date is None else '= ?'}
            AND tbl_note.rating_id {'IS NULL' if rating_id is None else '= ?'}
            AND tbl_note.comments {'IS NULL' if comments is None else '= ?'}
    """
    logger.debug(sql_select_id)
    values = []
    if user_id is not None:
        values.append(user_id)
    if book_id is not None:
        values.append(book_id)
    if reread is not None:
        values.append(reread)
    if status_id is not None:
        values.append(status_id)
    if finish_date is not None:
        values.append(finish_date)
    if rating_id is not None:
        values.append(rating_id)
    if comments is not None:
        values.append(comments)
    cur = conn.conn.execute(sql_select_id, values)
    db_row = cur.fetchone()
    logger.debug(f"Returned row {db_row}")
    note_id = None
    if db_row is not None:
        note_id = db_row[0]
    logger.debug(f"Existing note_id: {note_id}")
    return note_id


def update():
    pass
