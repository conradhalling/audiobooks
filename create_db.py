r"""
Load the data from the CSV file into the SQLite3 database.
The script will not load the data more than once.

EXAMPLE
    python3 create_db.py \
        --csv_file      data/audible.csv \
        --db_file       data/audiobooks.sqlite3 \
        --vendor        audible.com \
        --log_file      logs/create_db.log \
        --log_level     debug \
        --transaction   commit

ASSUMPTIONS
    -   Titles are unique.

TESTS
    -   Loading the data twice does not cause duplicated data.
    -   Calling db_test_foreign_key_enforcement() raises a
        sqlite3.IntegrityError exception.

TO DO
    -   Where do I track purchases?

        A book is acquired once from a vendor.
        A book can be acquired multiple times from different vendors.
        So the combinaton of book_id and vendor_id must be unique.

    -   tbl_book_acquisition
            id INTEGER PRIMARY KEY
            book_id NOT NULL
            vendor_id NOT NULL
            acquisition_type_id (f.k. to tbl_acquisition_type) NOT NULL
            audible_credits INTEGER NULL
            price_in_cents INTEGER NULL
            acquisition_date TEXT NOT NULL
            UNIQUE (book_id, vendor_id)
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
import sys
import textwrap
import traceback

import db.conn
import utils

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Convert an audibooks CSV file to a SQLite database",
        epilog=textwrap.dedent(rf"""
        Example:
          python3 {os.path.basename(__file__)} \
            --csv_file      data/audible.csv \
            --db_file       data/audiobooks.sqlite3 \
            --vendor        audible.com \
            --log_file      logs/create_db.log \
            --log_level     debug \
            --transaction   commit""")
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
        "--vendor",
        choices=["audible.com", "cloudLibrary"],
        help="audiobook vendor",
        required=True,
    )
    parser.add_argument(
        "--transaction",
        choices=["commit", "rollback"],
        help="commit or roll back changes to the database",
        required=True,
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


# CSV file processing code.

def save_authors(conn, authors_str):
    logger.debug(f"authors_str: '{authors_str}'")
    authors = authors_str.split(sep="&")
    logger.debug(f"authors: {authors}")
    author_ids = []
    for author in authors:
        author = author.strip()
        if author != "":
            author_id = db.author.save(author)
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
            narrator_id = db.narrator.save(narrator)
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
            translator_id = db.db.save_translator(conn, translator)
            translator_ids.append(translator_id)
    logger.debug(f"translator ids: {translator_ids}")
    return translator_ids


def save_book(title, pub_date, hours, minutes):
    logger.debug(f"title: '{title}'")
    logger.debug(f"pub_date: '{pub_date}'")
    logger.debug(f"hours: {hours}")
    logger.debug(f"minutes: {minutes}")
    if pub_date == "":
        pub_date = None
    book_id = db.book.save(title, pub_date, hours, minutes)
    logger.debug(f"book_id: {book_id}")
    return book_id


def save_data(csv_file, db_file, vendor, transaction):
    db.connect(db_file=db_file)
    db.enforce_foreign_key_constraints()
    db.begin_transaction()
    try:
        # Create tables.
        db.create_tables()

        # Save the vendor in the database.
        vendor_id = db.vendor.save(vendor)

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
                author_ids = save_authors(db.conn.conn, csv_authors)

                # Insert one or more new translators into tbl_translator.
                csv_translators = csv_row[2]
                logger.debug(f"csv_translators: '{csv_translators}'")
                translator_ids = save_translators(db.conn.conn, csv_translators)

                # Insert one or more new narrators into tbl_narrator.
                csv_narrators = csv_row[3]
                logger.debug(f"csv_narrators: '{csv_narrators}'")
                narrator_ids = save_narrators(db.conn.conn, csv_narrators)

                # Insert book attributes into tbl_book.
                csv_title = csv_row[0]
                csv_pub_date = csv_row[4]
                csv_hours = csv_row[5]
                csv_minutes = csv_row[6]
                logger.debug(f"csv_title: '{csv_title}'")
                logger.debug(f"csv_pub_date: '{csv_pub_date}'")
                logger.debug(f"hours: {csv_hours}")
                logger.debug(f"minutes: {csv_minutes}")
                book_id = save_book(csv_title, csv_pub_date, csv_hours, csv_minutes)

                # Insert book ID and associated author IDs into tbl_book_author.
                for author_id in author_ids:
                    db.db.save_book_author(db.conn.conn, book_id, author_id)
                
                # Insert book and associated translators into tbl_book_translators.
                for translator_id in translator_ids:
                    db.db.save_book_translator(db.conn.conn, book_id, translator_id)
                
                # Insert book and associated narrators into tbl_book_narrators.
                for narrator_id in narrator_ids:
                    db.db.save_book_narrator(db.conn.conn, book_id, narrator_id)
                
                # Insert book and associated vendor into tbl_book_vendor.
                db.db.save_book_vendor(db.conn.conn, book_id, vendor_id)
                db.db.save_book_vendor(db.conn.conn, book_id, vendor_id)

        # Commit or roll back database changes. If the rollback is successful,
        # the size of the database file will be 0 bytes.
        if transaction == "commit":
            print(f"Requested transaction is {transaction}: Committing changes...")
            db.commit()
            print("  Done.")
        else:
            print(f"Requested transaction is {transaction}: Rolling back changes...")
            db.rollback()
            print("  Done.")

    except Exception as exc:
        # Roll back changes if any exception occurred.
        print("Caught an exception. Rolling back changes...")
        db.rollback()
        print("  Done.")
        print(f"The exception was '{exc}'.")
        traceback.print_exc(file=sys.stdout)

    
    db.close()

def main():
    args = parse_args()
    utils.init_logging(args.log_file, args.log_level)
    save_data(args.csv_file, args.db_file, args.vendor, args.transaction)

if __name__ == "__main__":
    main()
