"""
SQLite3 database interaction code.
Functions are listed in alphabetical order.
"""

import logging
logger = logging.getLogger(__name__)


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


def create_tbl_book_vendor(conn):
    logger.debug("Creating tbl_book_vendor...")
    sql_create_tbl_book_vendor = """
        CREATE TABLE IF NOT EXISTS
        tbl_book_vendor
        (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            FOREIGN KEY (book_id) REFERENCES tbl_book(id),
            FOREIGN KEY (vendor_id) REFERENCES tbl_vendor(id),
            UNIQUE (book_id, vendor_id)
        )
    """
    conn.execute(sql_create_tbl_book_vendor)


def save_book_vendor(conn, book_id, vendor_id):
    sql_select_book_vendor_id = """
    SELECT
        tbl_book_vendor.id
    FROM
        tbl_book_vendor
    WHERE
        tbl_book_vendor.book_id = ?
        AND tbl_book_vendor.vendor_id = ?
    """
    sql_insert_book_vendor = """
    INSERT INTO
        tbl_book_vendor
        (
            book_id,
            vendor_id
        )
        VALUES (?, ?)
    """
    logger.debug(f"book_id: {book_id}; vendor_id: {vendor_id}")

    # Is the book_id-vendor_id combination already in tbl_book_vendor?
    cur = conn.execute(sql_select_book_vendor_id, (book_id, vendor_id,))
    db_row = cur.fetchone()
    logger.debug(f"book_vendor_id: {db_row}")
    if db_row is not None:
        book_vendor_id = db_row[0]
        logger.debug(f"existing book_vendor_id: {book_vendor_id}")
    else:
        logger.debug(f"Inserting book_id {book_id} and vendor_id {vendor_id} into tbl_book_vendor...")
        cur = conn.execute(sql_insert_book_vendor, (book_id, vendor_id,))
        book_vendor_id = cur.lastrowid
        logger.debug(f"new book_vendor_id: {book_vendor_id}")
    logger.debug(f"book_vendor_id: {book_vendor_id}")
    return book_vendor_id
