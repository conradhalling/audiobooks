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

ASSUMPTIONS
    -   Titles are unique.

TESTS
    -   Loading the data twice does not cause duplicated data.
    -   Calling db_test_foreign_key_enforcement() raises a
        sqlite3.IntegrityError exception.

TO DO
    -   Where do I track purchases?
    -   Update my ratings for a 0 to 5 scale.
    -   tbl_book_vendor
            book_vendor_id INTEGER PRIMARY KEY
            book_id NOT NULL
            vendor_id NOT NULL
            purchase_type_id (f.k. to tbl_purchase_type) NOT NULL
            audible_credits INTEGER NULL
            price_in_cents INTEGER NULL
    -   tbl_acquisition
            id
            acquisition_type_id (fk tbl_acquisition_type(id))
            charge_amount_cents INTEGER
            acquisition_date
    -   tbl_event_type
            id
            event_type TEXT NOT NULL
            1   'started'
            2   'finished'
    -   tbl_event
            id INTEGER PRIMARY KEY
            book_id INTEGER NOT NULL
            event_type_id INTEGER NOT NULL
            date TEXT NOT NULL
    -   tbl_book_rating
            id INTEGER PRIMARY KEY
            book_id INTEGER NOT NULL (fk)
            rating_id INTEGER NOT NULL (fk)
            notes TEXT
    -   How to manage identical titles (Serkis and Inglis narrations of The
        Fellowship of the Ring, for example). Can I come up with a unique key
        that is a combination of title and narrator?
    -   Move the database interaction code into its own module.
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
    format = "[%(filename)s:%(lineno)4d - %(funcName)35s() ] %(levelname)s: %(message)s"
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
    db_create_tbl_author(conn)
    db_create_tbl_narrator(conn)
    db_create_tbl_translator(conn)
    db_create_tbl_book(conn)
    db_create_tbl_book_author(conn)
    db_create_tbl_book_narrator(conn)
    db_create_tbl_book_translator(conn)
    db_create_tbl_vendor(conn)
    db_create_tbl_acquisition_type(conn)
    db_create_tbl_rating(conn)


def db_create_tbl_acquisition_type(conn):
    logger.debug("Creating tbl_acqusition_type...")
    sql_create_tbl_acquisition_type = """
        CREATE TABLE IF NOT EXISTS
        tbl_acquisition_type
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """
    conn.execute(sql_create_tbl_acquisition_type)
    acquisition_types = ['vendor credit', 'charge', 'no charge']
    for acquisition_type in acquisition_types:
        db_save_acquisition_type(conn, acquisition_type)


def db_create_tbl_author(conn):
    logger.debug("Creating table tbl_author...")
    sql_create_tbl_author = """
        CREATE TABLE IF NOT EXISTS
        tbl_author
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )"""
    conn.execute(sql_create_tbl_author)


def db_create_tbl_book(conn):
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


def db_create_tbl_book_author(conn):
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


def db_create_tbl_book_narrator(conn):
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


def db_create_tbl_book_translator(conn):
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


def db_create_tbl_narrator(conn):
    logger.debug("Creating table tbl_narrator...")
    sql_create_tbl_narrator = """
        CREATE TABLE IF NOT EXISTS
        tbl_narrator
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )"""
    conn.execute(sql_create_tbl_narrator)


def db_create_tbl_rating(conn):
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
        db_save_rating(conn, rating[0], rating[1])


def db_create_tbl_translator(conn):
    logger.debug("Creating table tbl_translator...")
    sql_create_tbl_translator = """
        CREATE TABLE IF NOT EXISTS
        tbl_translator
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """
    conn.execute(sql_create_tbl_translator)


def db_create_tbl_vendor(conn):
    logger.debug("Creating tbl_vendor...")
    sql_create_tbl_vendor = """
        CREATE TABLE IF NOT EXISTS
        tbl_vendor
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """
    conn.execute(sql_create_tbl_vendor)
    vendors = ["audible.com", "cloudLibrary"]
    for vendor in vendors:
        db_save_vendor(conn, vendor)


def db_save_acquisition_type(conn, acquisition_type):
    sql_select_acquisition_type_id = """
        SELECT
            tbl_acquisition_type.id
        FROM
            tbl_acquisition_type
        WHERE
            tbl_acquisition_type.name = ?
    """
    sql_insert_acquisition_type = """
        INSERT INTO tbl_acquisition_type
        (
            name
        )
        VALUES (?)
    """
    logger.debug(f"acquisition_type: '{acquisition_type}'")

    # Is the acquisition_type already in tbl_acquisition_type?
    cur = conn.execute(sql_select_acquisition_type_id, (acquisition_type,))
    db_row = cur.fetchone()
    logger.debug(f"acquisition_type_id: {db_row}")
    if db_row is not None:
        acquisition_type_id = db_row[0]
        logger.debug(f"existing acquisition_type_id: {acquisition_type_id}")
    else:
        # Insert a new acquisition type.
        logger.debug(f"Inserting '{acquisition_type}' into tbl_acquisition_type")
        cur = conn.execute(sql_insert_acquisition_type, (acquisition_type,))
        acquisition_type_id = cur.lastrowid
        logger.debug(f"new acquisition_type_id: {acquisition_type_id}")
    logger.debug(f"acquisition_type_id: {acquisition_type_id}")
    return acquisition_type_id


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


def db_save_book_narrator(conn, book_id, narrator_id):
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


def db_save_book_translator(conn, book_id, translator_id):
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


def db_save_narrator(conn, narrator):
    sql_select_narrator_id = """
        SELECT
            tbl_narrator.id
        FROM
            tbl_narrator
        WHERE
            tbl_narrator.name = ?
    """
    sql_insert_narrator = """
        INSERT INTO tbl_narrator
        (
            name
        )
        VALUES (?)
    """
    logger.debug(f"narrator: '{narrator}'")

    # Is the narrator already in tbl_narrator?
    cur = conn.execute(sql_select_narrator_id, (narrator,))
    db_row = cur.fetchone()
    logger.debug(f"narrator_id: {db_row}")
    if db_row is not None:
        narrator_id = db_row[0]
        logger.debug(f"existing narrator_id: {narrator_id}")
    else:
        # Insert a new narrator.
        logger.debug(f"Inserting '{narrator}' into tbl_narrator")
        cur = conn.execute(sql_insert_narrator, (narrator,))
        narrator_id = cur.lastrowid
        logger.debug(f"new narrator_id: {narrator_id}")
    logger.debug(f"narrator_id: {narrator_id}")
    return narrator_id


def db_save_rating(conn, stars, description):
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


def db_save_translator(conn, translator):
    sql_select_translator_id = """
        SELECT
            tbl_translator.id
        FROM
            tbl_translator
        WHERE
            tbl_translator.name = ?
    """
    sql_insert_translator = """
        INSERT INTO tbl_translator
        (
            name
        )
        VALUES (?)
    """
    logger.debug(f"translator: '{translator}'")

    # Is the translator already in tbl_translator?
    cur = conn.execute(sql_select_translator_id, (translator,))
    db_row = cur.fetchone()
    logger.debug(f"translator_id: {db_row}")
    if db_row is not None:
        translator_id = db_row[0]
        logger.debug(f"existing translator_id: {translator_id}")
    else:
        # Insert a new translator.
        logger.debug(f"Inserting '{translator}' into tbl_translator")
        cur = conn.execute(sql_insert_translator, (translator,))
        translator_id = cur.lastrowid
        logger.debug(f"new translator_id: {translator_id}")
    logger.debug(f"translator_id: {translator_id}")
    return translator_id


def db_save_vendor(conn, vendor):
    sql_select_vendor_id = """
        SELECT
            tbl_vendor.id
        FROM
            tbl_vendor
        WHERE
            tbl_vendor.name = ?
    """
    sql_insert_vendor = """
        INSERT INTO tbl_vendor
        (
            name
        )
        VALUES (?)
    """
    logger.debug(f"vendor: '{vendor}'")

    # Is the vendor already in tbl_vendor?
    cur = conn.execute(sql_select_vendor_id, (vendor,))
    db_row = cur.fetchone()
    logger.debug(f"vendor_id: {db_row}")
    if db_row is not None:
        vendor_id = db_row[0]
        logger.debug(f"existing vendor_id: {vendor_id}")
    else:
        # Insert a new vendor.
        logger.debug(f"Inserting '{vendor}' into tbl_vendor")
        cur = conn.execute(sql_insert_vendor, (vendor,))
        vendor_id = cur.lastrowid
        logger.debug(f"new vendor_id: {vendor_id}")
    logger.debug(f"vendor_id: {vendor_id}")
    return vendor_id


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
        if author != "":
            author_id = db_save_author(conn, author)
            author_ids.append(author_id)
    logger.debug(f"author ids: {author_ids}")
    return author_ids


def save_narrators(conn, narrators_str):
    logger.debug(f"narrators_str: '{narrators_str}'")
    narrators = narrators_str.split(sep="&")
    logger.debug(f"narrators: {narrators}")
    narrator_ids = []
    for narrator in narrators:
        narrator = narrator.strip()
        if narrator != "":
            narrator_id = db_save_narrator(conn, narrator)
            narrator_ids.append(narrator_id)
    logger.debug(f"narrator ids: {narrator_ids}")
    return narrator_ids


def save_translators(conn, translators_str):
    logger.debug(f"translators_str: '{translators_str}'")
    translators = translators_str.split(sep="&")
    logger.debug(f"translators: {translators}")
    translator_ids = []
    for translator in translators:
        translator = translator.strip()
        if translator != "":
            translator_id = db_save_translator(conn, translator)
            translator_ids.append(translator_id)
    logger.debug(f"translator ids: {translator_ids}")
    return translator_ids


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

            # Insert one or more new translators into tbl_translator.
            csv_translators = csv_row[2]
            logger.debug(f"csv_translators: '{csv_translators}'")
            translator_ids = save_translators(conn, csv_translators)

            # Insert one or more new authors into tbl_author.
            csv_narrators = csv_row[3]
            logger.debug(f"csv_narrators: '{csv_narrators}'")
            narrator_ids = save_narrators(conn, csv_narrators)

            # Insert title into tbl_book.
            csv_title = csv_row[0]
            csv_pub_date = csv_row[4]
            csv_hours = csv_row[5]
            csv_minutes = csv_row[6]
            logger.debug(f"csv_title: '{csv_title}'")
            logger.debug(f"csv_pub_date: '{csv_pub_date}'")
            logger.debug(f"hours: '{csv_hours}'")
            logger.debug(f"minutes: '{csv_minutes}'")
            book_id = save_book(conn, csv_title, csv_pub_date, csv_hours, csv_minutes)

            # Insert book ID and associated author IDs into tbl_book_author.
            for author_id in author_ids:
                db_save_book_author(conn, book_id, author_id)
            
            # Insert book and associated translators into tbl_book_translators.
            for translator_id in translator_ids:
                db_save_book_translator(conn, book_id, translator_id)
            
            # Insert book and associated narrators into tbl_book_narrators.
            for narrator_id in narrator_ids:
                db_save_book_narrator(conn, book_id, narrator_id)

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
