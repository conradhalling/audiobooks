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
    -   Calling db.test_foreign_key_enforcement() raises a
        sqlite3.IntegrityError exception.

TO DO
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
"""


import argparse
import csv
import logging
import os
import sys
import textwrap
import traceback

import csv_processor    # csv_processor.load_csv_data loads CSV data into
                        # the database
import db.conn          # db.conn.conn contains the sqlite3.Connection object.
import utils            # utils.init_logging initializes the logger.

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


def main():
    args = parse_args()
    utils.init_logging(args.log_file, args.log_level)
    db.connect(db_file=args.db_file)
    db.begin_transaction()
    try:
        db.create_schema()
        csv_processor.load_csv_data(args.csv_file, args.vendor)
        # Commit or roll back database changes. If the rollback is successful,
        # the size of the database file will be 0 bytes.
        if args.transaction == "commit":
            print(f"Requested transaction is {args.transaction}: Committing changes...")
            db.commit()
            print("  Done.")
        else:
            print(f"Requested transaction is {args.transaction}: Rolling back changes...")
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


if __name__ == "__main__":
    main()
