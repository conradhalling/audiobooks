"""
SQLite3 database interaction code.
Functions are listed in alphabetical order.
"""

import logging
import sqlite3

import db

logger = logging.getLogger(__name__)


def create_tables(conn):
    db.author.create_table(conn)
    db.narrator.create_table(conn)
    db.translator.create_table(conn)
    db.book.create_table(conn)
    create_tbl_book_author(conn)
    create_tbl_book_narrator(conn)
    create_tbl_book_translator(conn)
    db.vendor.create_table(conn)
    create_tbl_acquisition_type(conn)
    create_tbl_rating(conn)


def create_tbl_acquisition_type(conn):
    logger.debug("Creating tbl_acqusition_type...")
    sql_create_tbl_acquisition_type = """
        CREATE TABLE IF NOT EXISTS
        tbl_acquisition_type
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """
    conn.execute(sql_create_tbl_acquisition_type)
    acquisition_types = ['vendor credit', 'charge', 'no charge']
    for acquisition_type in acquisition_types:
        save_acquisition_type(conn, acquisition_type)


def create_tbl_book_author(conn):
    logger.debug("Creating tbl_book_author...")
    sql_create_tbl_book_author = """
        CREATE TABLE IF NOT EXISTS
        tbl_book_author
        (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (author_id) REFERENCES tbl_author(id)
        )
    """
    conn.execute(sql_create_tbl_book_author)


def create_tbl_book_narrator(conn):
    logger.debug("Creating tbl_book_narrator...")
    sql_create_tbl_book_narrator = """
        CREATE TABLE IF NOT EXISTS
        tbl_book_narrator
        (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            narrator_id INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (narrator_id) REFERENCES tbl_narrator(id)
        )
    """
    conn.execute(sql_create_tbl_book_narrator)


def create_tbl_book_translator(conn):
    logger.debug("Creating tbl_book_translator...")
    sql_create_tbl_book_translator = """
        CREATE TABLE IF NOT EXISTS
        tbl_book_translator
        (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            translator_id INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (translator_id) REFERENCES tbl_translator(id)
        )
    """
    conn.execute(sql_create_tbl_book_translator)


def create_tbl_rating(conn):
    logger.debug("Creating table tbl_rating...")
    sql_create_tbl_rating = """
        CREATE TABLE IF NOT EXISTS
        tbl_rating
        (
            id INTEGER PRIMARY KEY,
            stars INTEGER NOT NULL,
            description TEXT NOT NULL
        )
    """
    conn.execute(sql_create_tbl_rating)
    ratings = [
        (0, "very bad",),
        (1, "poor",),
        (2, "meh",),
        (3, "good",),
        (4, "very good",),
        (5, "excellent",),
    ]
    for rating in ratings:
        save_rating(conn, rating[0], rating[1])


def insert_acquisition_type(conn, acquisition_type):
    logger.debug(f"acquisition_type: '{acquisition_type}'")
    sql_insert_acquisition_type = """
        INSERT INTO tbl_acquisition_type
        (
            name
        )
        VALUES (?)
    """
    # Insert a new acquisition type.
    logger.debug(f"Inserting '{acquisition_type}' into tbl_acquisition_type")
    cur = conn.execute(sql_insert_acquisition_type, (acquisition_type,))
    acquisition_type_id = cur.lastrowid
    logger.debug(f"New acquisition_type_id: {acquisition_type_id}")
    return acquisition_type_id


def save_acquisition_type(conn, acquisition_type):
    logger.debug(f"acquisition_type: '{acquisition_type}'")
    acquisition_type_id = select_acquistion_type_id(conn, acquisition_type)
    if acquisition_type_id is None:
        acquisition_type_id = insert_acquisition_type(conn, acquisition_type)
    logger.debug(f"Saved acquisition_type_id: {acquisition_type_id}")
    return acquisition_type_id


def select_acquistion_type_id(conn, acquisition_type):
    logger.debug(f"acquisition_type: '{acquisition_type}'")
    sql_select_acquisition_type_id = """
        SELECT
            tbl_acquisition_type.id
        FROM
            tbl_acquisition_type
        WHERE
            tbl_acquisition_type.name = ?
    """
    cur = conn.execute(sql_select_acquisition_type_id, (acquisition_type,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for acquisition_type_id: {db_row}")
    acquisition_type_id = None
    if db_row is not None:
        acquisition_type_id = db_row[0]
    logger.debug(f"Existing acquistion_type_id: {acquisition_type_id}")
    return acquisition_type_id


def save_book_author(conn, book_id, author_id):
    sql_select_book_author_id = """
    SELECT
        tbl_book_author.id
    FROM
        tbl_book_author
    WHERE
        tbl_book_author.book_id = ?
        AND tbl_book_author.author_id = ?
    """
    sql_insert_book_author = """
    INSERT INTO
        tbl_book_author
        (
            book_id,
            author_id
        )
        VALUES (?, ?)
    """
    logger.debug(f"book_id: {book_id}; author_id: {author_id}")

    # Is the book_id-author_id combination already in tbl_book_author?
    cur = conn.execute(sql_select_book_author_id, (book_id, author_id,))
    db_row = cur.fetchone()
    logger.debug(f"book_author_id: {db_row}")
    if db_row is not None:
        book_author_id = db_row[0]
        logger.debug(f"existing book_author_id: {book_author_id}")
    else:
        logger.debug(f"Inserting book_id {book_id} and author_id {author_id} into tbl_book_author...")
        cur = conn.execute(sql_insert_book_author, (book_id, author_id,))
        book_author_id = cur.lastrowid
        logger.debug(f"new book_author_id: {book_author_id}")
    logger.debug(f"book_author_id: {book_author_id}")
    return book_author_id


def save_book_narrator(conn, book_id, narrator_id):
    sql_select_book_narrator_id = """
    SELECT
        tbl_book_narrator.id
    FROM
        tbl_book_narrator
    WHERE
        tbl_book_narrator.book_id = ?
        AND tbl_book_narrator.narrator_id = ?
    """
    sql_insert_book_narrator = """
    INSERT INTO
        tbl_book_narrator
        (
            book_id,
            narrator_id
        )
        VALUES (?, ?)
    """
    logger.debug(f"book_id: {book_id}; narrator_id: {narrator_id}")

    # Is the book_id-narrator_id combination already in tbl_book_narrator?
    cur = conn.execute(sql_select_book_narrator_id, (book_id, narrator_id,))
    db_row = cur.fetchone()
    logger.debug(f"book_narrator_id: {db_row}")
    if db_row is not None:
        book_narrator_id = db_row[0]
        logger.debug(f"existing book_narrator_id: {book_narrator_id}")
    else:
        logger.debug(f"Inserting book_id {book_id} and narrator_id {narrator_id} into tbl_book_narrator...")
        cur = conn.execute(sql_insert_book_narrator, (book_id, narrator_id,))
        book_narrator_id = cur.lastrowid
        logger.debug(f"new book_narrator_id: {book_narrator_id}")
    logger.debug(f"book_narrator_id: {book_narrator_id}")
    return book_narrator_id


def save_book_translator(conn, book_id, translator_id):
    sql_select_book_translator_id = """
    SELECT
        tbl_book_translator.id
    FROM
        tbl_book_translator
    WHERE
        tbl_book_translator.book_id = ?
        AND tbl_book_translator.translator_id = ?
    """
    sql_insert_book_translator = """
    INSERT INTO
        tbl_book_translator
        (
            book_id,
            translator_id
        )
        VALUES (?, ?)
    """
    logger.debug(f"book_id: {book_id}; translator_id: {translator_id}")

    # Is the book_id-translator_id combination already in tbl_book_translator?
    cur = conn.execute(sql_select_book_translator_id, (book_id, translator_id,))
    db_row = cur.fetchone()
    logger.debug(f"book_translator_id: {db_row}")
    if db_row is not None:
        book_translator_id = db_row[0]
        logger.debug(f"existing book_translator_id: {book_translator_id}")
    else:
        logger.debug(f"Inserting book_id {book_id} and translator_id {translator_id} into tbl_book_translator...")
        cur = conn.execute(sql_insert_book_translator, (book_id, translator_id,))
        book_translator_id = cur.lastrowid
        logger.debug(f"new book_translator_id: {book_translator_id}")
    logger.debug(f"book_translator_id: {book_translator_id}")
    return book_translator_id


def save_rating(conn, stars, description):
    sql_select_rating_id = """
        SELECT
            tbl_rating.id
        FROM
            tbl_rating
        WHERE
            tbl_rating.stars = ?
            and tbl_rating.description = ?
    """
    sql_insert_rating = """
        INSERT INTO tbl_rating
        (
            stars,
            description
        )
        VALUES (?, ?)
    """
    logger.debug(f"rating: ({stars}, '{description}'")

    # Is the rating already in tbl_rating?
    cur = conn.execute(sql_select_rating_id, (stars, description,))
    db_row = cur.fetchone()
    logger.debug(f"rating_id: {db_row}")
    if db_row is not None:
        rating_id = db_row[0]
        logger.debug(f"existing rating_id: {rating_id}")
    else:
        # Insert a new rating.
        logger.debug(f"Inserting '({stars}, '{description}' into tbl_rating")
        cur = conn.execute(sql_insert_rating, (stars, description,))
        rating_id = cur.lastrowid
        logger.debug(f"new rating_id: {rating_id}")
    logger.debug(f"rating_id: {rating_id}")
    return rating_id


def enforce_foreign_key_constraints(conn):
    """
    Set PRAGMA foreign_keys = ON.
    """
    cur = conn.cursor()
    # Set the pragma.
    if conn.in_transaction == True:
        # This is needed when conn.autocommit is False because a transaction
        # is already open, and PRAGMA foreign_keys = ON has no effect in
        # an open transaction.
        cur.executescript("COMMIT; PRAGMA foreign_keys = ON; BEGIN;")
    else:
        cur.execute("PRAGMA foreign_keys = ON")
    cur.close()
    verify_foreign_key_constraints(conn)


def verify_foreign_key_constraints(conn):
    """
    Verify that the PRAGMA foreign_keys value is 1.
    Raise a sqlite3.IntegrityError exception if the value is not 1.
    """
    # Get the pragma. It must be 1.
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys")
    rows = cur.fetchall()
    cur.close()
    pragma_foreign_keys_value = None
    if len(rows) != 0:
        pragma_foreign_keys_value = rows[0][0]
    logger.debug(f"pragma_foreign_keys_value: {pragma_foreign_keys_value}")
    if pragma_foreign_keys_value != 1:
        raise sqlite3.IntegrityError("PRAGMA foreign_keys is not ON")
