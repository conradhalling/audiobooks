r"""
Read the audible.csv data file and save the data in the SQLite3 database.
The script will not load the data more than once.

EXAMPLE
    python3 save_cloudlibrarydata.py \
        --csv_file      data/cloudlibrary.csv \
        --db_file       data/audiobooks.sqlite3 \
        --log_file      logs/save_cloudlibrary_data.log \
        --log_level     debug \
        --transaction   commit
"""


import argparse
import logging
import os
import sys
import textwrap
import traceback

import dotenv
dotenv.load_dotenv()

import cloudlibrary_processor   # cloudlibrary_processor.save_data loads CSV
                                # data into the database
import db                       # db interacts with the SQLite3 database.
import utils                    # utils.init_logging initializes the logger

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Save cloudLibrary audiobooks data to the SQLite3 database",
        epilog=textwrap.dedent(rf"""
        Example:
          python3 {os.path.basename(__file__)} \
            --csv_file      data/cloudlibrary.csv \
            --db_file       data/audiobooks.sqlite3 \
            --log_file      logs/save_cloudlibrary_data.log \
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

    # Raise an exception if username or password is not verified.
    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')
    db.user.verify_username_password(username, password)

    # Process the data using a database transaction.
    db.begin_transaction()
    try:
        cloudlibrary_processor.save_data(username, args.csv_file)
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
