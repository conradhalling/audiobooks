r"""
This script is based on a combination of sqlite/autocommit.py
and sqlite/create_db.py.

EXAMPLE
    # Save data:
    python3 create_db.py \
        --csv_file   data/audible.csv \
        --db_file    data/audiobooks.sqlite3 \
        --log_file   log/create_db.log \
        --log_level  debug \
        --commit

ASSUMPTION
    Titles are unique.

TESTS
    -   Loading the data twice does not cause duplicated data.
    -   Calling db_test_foreign_key_enforcement() raises a
        sqlite3.IntegrityError exception.

TO DO
    -   Add a column for translator.
"""

import argparse
import csv
import logging
import os
import sqlite3
import sys
import textwrap

logger = logging.getLogger(__name__)


def init_logging(log_file, log_level):
    logging_numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(logging_numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    format = "[%(filename)s:%(lineno)4d - %(funcName)20s() ] %(levelname)s: %(message)s"
    logging.basicConfig(
        filename=log_file,
        encoding='utf-8',
        format=format,
        level=logging_numeric_level)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Convert an audibooks CSV file to a SQLite database",
        epilog=textwrap.dedent(f"""
        Example:
          python3 {os.path.basename(__file__)} \\
            --csv_file   audible.csv \\
            --db_file    audiobooks.sqlite3 \\
            --log_file   log/create_db.log \\
            --log_level  info \\
          [ --commit ]""")
    )
    parser.add_argument(
        "--csv_file",
        help="input CSV file",
        required=True,
    )
    parser.add_argument(
        "--db_file",
        help="sqlite3 database file",
        required=True,
    )
    parser.add_argument(
        "--commit",
        help="commit changes to the database",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--log_file",
        help="output log file",
        required=True,
    )
    parser.add_argument(
        "--log_level",
        choices=["debug", "info", "warning", "error", "critical"],
        help="logging level",
        required=True,
    )
    args = parser.parse_args()
    return args


##############################################################################
# Database code.


def db_create_tables(conn):
    logger.debug("Creating table tbl_author...")
    sql_create_tbl_author = """
        CREATE TABLE IF NOT EXISTS
        tbl_author
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )"""
    conn.execute(sql_create_tbl_author)

    logger.debug("Creating table tbl_book...")
    sql_create_tbl_book = """
        CREATE TABLE IF NOT EXISTS
        tbl_book
        (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL UNIQUE,
            pub_date TEXT,
            hours INTEGER NOT NULL,
            minutes INTEGER NOT NULL
        )
    """
    conn.execute(sql_create_tbl_book)

    logger.debug("Creating tbl_book_author...")
    sql_create_tbl_book_author = """
        CREATE TABLE IF NOT EXISTS
        tbl_book_author
        (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (author_id) REFERENCES tbl_author(id),
            FOREIGN KEY (book_id) REFERENCES tbl_book(id)
        )
    """
    conn.execute(sql_create_tbl_book_author)


def db_save_author(conn, author):
    sql_select_author_id = """
        SELECT
            tbl_author.id
        FROM
            tbl_author
        WHERE
            tbl_author.name = ?
    """
    sql_insert_author = """
        INSERT INTO tbl_author
        (
            name
        )
        VALUES (?)
    """
    logger.debug(f"author: '{author}'")

    # Is the author already in tbl_author?
    cur = conn.execute(sql_select_author_id, (author,))
    db_row = cur.fetchone()
    logger.debug(f"author_id: {db_row}")
    if db_row is not None:
        author_id = db_row[0]
        logger.debug(f"existing author_id: {author_id}")
    else:
        # Insert a new author.
        logger.debug(f"Inserting '{author}' into tbl_author")
        cur = conn.execute(sql_insert_author, (author,))
        author_id = cur.lastrowid
        logger.debug(f"new author_id: {author_id}")
    logger.debug(f"author_id: {author_id}")
    return author_id


def db_save_book(conn, title, pub_date, hours, minutes):
    sql_select_book_id = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
        WHERE
            tbl_book.title = ?
    """
    sql_insert_book = """
        INSERT INTO tbl_book
        (
            title,
            pub_date,
            hours,
            minutes
        )
        VALUES (?, ?, ?, ?)
    """
    logger.debug(f"title: '{title}'")
    logger.debug(f"pub_date: {pub_date}")
    logger.debug(f"hours: {hours}")
    logger.debug(f"minutes: {minutes}")

    # Is the book already in tbl_book?
    cur = conn.execute(sql_select_book_id, (title,))
    db_row = cur.fetchone()
    logger.debug(f"book_id: {db_row}")
    if db_row is not None:
        book_id = db_row[0]
        logger.debug(f"existing book_id: {book_id}")
    else:
        # Insert a new book.
        logger.debug(f"Inserting '{title}' into tbl_book...")
        cur = conn.execute(sql_insert_book, (title, pub_date, hours, minutes))
        book_id = cur.lastrowid
        logger.debug(f"new book_id: {book_id}")
    logger.debug(f"book_id: {book_id}")
    return book_id


def db_save_book_author(conn, book_id, author_id):
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


def db_test_foreign_key_enforcement(conn):
    # Attempt to delete a row from table authors.
    # This should cause a foreign key constraint problem.
    print("Attempting to violate foreign key constraint...")
    sql_delete_author = """
        DELETE from tbl_author
        WHERE id = 1
    """
    try:
        conn.execute(sql_delete_author)
        print("  Foreign key constraint not enforced!")
    except sqlite3.IntegrityError as exc:
        print("  ", type(exc).__name__, ": ", exc, sep="")


###############################################################################
# CSV file processing code.

def save_authors(conn, authors_str):
    logger.debug(f"authors_str: '{authors_str}'")
    authors = authors_str.split(sep="&")
    logger.debug(f"authors: {authors}")
    author_ids = []
    for author in authors:
        author = author.strip()
        author_id = db_save_author(conn, author)
        author_ids.append(author_id)
    logger.debug(f"author ids: {author_ids}")
    return author_ids


def save_book(conn, title, pub_date, hours, minutes):
    logger.debug(f"title: '{title}'")
    logger.debug(f"pub_date: '{pub_date}'")
    logger.debug(f"hours: {hours}")
    logger.debug(f"minutes: {minutes}")
    if pub_date == "":
        pub_date = None
    book_id = db_save_book(conn, title, pub_date, hours, minutes)
    logger.debug(f"book_id: {book_id}")
    return book_id


def save_data(csv_file, db_file, commit_flag):
    # Open a connection.
    conn = sqlite3.connect(database=db_file, autocommit=True)

    # Enforce foreign key constraints.
    sql_pragma_foreign_keys = "PRAGMA foreign_keys = ON"
    conn.execute(sql_pragma_foreign_keys)

    # Begin an explicit transaction.
    sql_begin_transaction = "BEGIN TRANSACTION"
    conn.execute(sql_begin_transaction)

    # Create tables.
    db_create_tables(conn)

    with open(csv_file, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        # Skip the header line.
        row = next(csv_reader)
        # Process the data lines. The author name is in column 1.
        # Multiple authors are separated by the "&" character.
        # Save the tbl_author.id values for later use to associate
        # to the book.
        for csv_row in csv_reader:
            # Insert one or more new authors into tbl_author.
            csv_authors = csv_row[1]
            logger.debug(f"csv_authors: '{csv_authors}'")
            author_ids = save_authors(conn, csv_authors)

            # Insert title into tbl_book.
            csv_title = csv_row[0]
            csv_pub_date = csv_row[2]
            csv_hours = csv_row[3]
            csv_minutes = csv_row[4]
            logger.debug(f"csv_title: '{csv_title}'")
            logger.debug(f"csv_pub_date: '{csv_pub_date}'")
            logger.debug(f"hours: '{csv_hours}'")
            logger.debug(f"minutes: '{csv_minutes}'")
            book_id = save_book(conn, csv_title, csv_pub_date, csv_hours, csv_minutes)

            # Insert book ID and associated author IDs into tbl_book_author.
            for author_id in author_ids:
                db_save_book_author(conn, book_id, author_id)

    # Test enforcement of foreign key constraints.
    db_test_foreign_key_enforcement(conn)

    # Commit or roll back database changes. If the rollback is successful, the
    # size of the database file will be 0 bytes.
    if commit_flag:
        print("Committing changes...")
        conn.execute("COMMIT")
        print("  Done.")
        print(f"  The file {db_file} should contain the data.")
    else:
        print("Rolling back changes...")
        conn.execute("ROLLBACK")
        print("  Done.")
        print(f"  The file {db_file} should be empty.")
    
    # Clean up.
    conn.close()

def main():
    # Require Python 3.12 or 3.13 to use the autocommit attribute.
    # assert sys.version_info >= (3, 12)
    if sys.version_info.major != 3 or sys.version_info.minor < 12:
        raise ValueError("This script requires Python >= 3.12.")
    args = parse_args()
    init_logging(args.log_file, args.log_level)
    save_data(args.csv_file, args.db_file, args.commit)

if __name__ == "__main__":
    main()
