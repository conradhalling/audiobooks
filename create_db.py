r"""
This script is based on a combination of sqlite/autocommit.py
and sqlite/create_db.py.

EXAMPLE
    # Save data:
    python3 create_db.py \
        --csv_file   data/audible.csv \
        --db_file    data/audiobooks.sqlite3 \
        --log_level  debug \
        --commit

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


def init_logging(log_level):
    (long_base_name, extension) = os.path.splitext(__file__)
    short_base_name = os.path.basename(long_base_name)
    log_file_name = short_base_name + ".log"
    logging_numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(logging_numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    format = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(
        filename=log_file_name,
        encoding='utf-8',
        format=format,
        level=logging_numeric_level)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Convert a domains CSV file to an HTML file",
        epilog=textwrap.dedent(f"""
        Example:
          python3 {os.path.basename(__file__)} \\
            --csv_file   audible.csv \\
            --db_file    audiobooks.sqlite3 \\
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
        "--log_level",
        choices=["debug", "info", "warning", "error", "critical"],
        help="logging level",
        required=True,
    )
    args = parser.parse_args()
    return args


def save_author_data(cur, csv_file):
    logger.debug("Creating table tbl_author...")
    sql03 = """
        CREATE TABLE IF NOT EXISTS
        tbl_author
        (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )"""
    cur.execute(sql03)

    sql04 = """
        SELECT
            tbl_author.id
        FROM
            tbl_author
        WHERE
            tbl_author.name = ?"""
    sql05 = """
        INSERT INTO tbl_author
        (
            name
        )
        VALUES (?)"""

    with open(csv_file, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        # Skip the header line.
        row = next(csv_reader)
        # Process the data lines. The author name is in column 1.
        # Multiple authors are separated by the "&" character.
        for csv_row in csv_reader:
            csv_author = csv_row[1]
            logger.debug(f"csv_author: '{csv_author}'")
            authors = csv_author.split(sep="&")
            logger.debug(f"authors: {authors}")
            for author in authors:
                author = author.strip()
                # Is the author already in tbl_author?
                cur.execute(sql04, (author,))
                db_row = cur.fetchone()
                logger.debug(f"author_id: {db_row}")
                if db_row is None:
                    # Insert a new author.
                    logger.debug(f"Inserting '{author}' into tbl_author")
                    cur.execute(sql05, (author,))

def save_data(csv_file, db_file, commit_flag):
    # Open a connection.
    conn = sqlite3.connect(database=db_file, autocommit=True)

    # Enforce foreign key constraints.
    sql01 = "PRAGMA foreign_keys = ON"
    conn.execute(sql01)

    # Begin an explicit transaction.
    sql02 = "BEGIN TRANSACTION"
    conn.execute(sql02)

    # Get a cursor.
    cur = conn.cursor()

    # Save author data.
    save_author_data(cur, csv_file)

    # logger.debug("Creating table tbl_book...")
    # sql04 = """
    #     CREATE TABLE IF NOT EXISTS
    #     tbl_book
    #     (
    #         id INTEGER PRIMARY KEY,
    #         title TEXT,
    #         author_id INTEGER,
    #         FOREIGN KEY(author_id) REFERENCES tbl_author(id)
    #     )"""
    # cur.execute(sql04)

    # books_list = [
    #     ("Dawn", "Octavia", "Butler"),
    #     ("Foundation", "Isaac", "Asimov"),
    #     ("Ancillary Justice", "Anne", "Leckie"),
    # ]
    # sql06 = """
    #     SELECT
    #         id
    #     FROM
    #         authors
    #     WHERE
    #         first_name = ?
    #         AND last_name = ?"""
    # sql07 = """
    #     INSERT INTO
    #     books
    #     (
    #         title,
    #         author_id
    #     )
    #     VALUES (?, ?)"""

    # for row in books_list:
    #     cur.execute(sql06, (row[1], row[2]))
    #     author_id = cur.fetchone()[0]
    #     cur.execute(sql07, (row[0], author_id))
    # print("  Done.")

    # # Attempt to delete a row from table authors.
    # # This should cause a foreign key constraint problem.
    # print("Attempting to violate foreign key constraint...")
    # sql08 = """
    #     DELETE from authors
    #     WHERE id = 1
    # """
    # try:
    #     cur.execute(sql08)
    #     print("  Foreign key constraint not enforced!")
    # except sqlite3.IntegrityError as exc:
    #     print("  ", type(exc).__name__, ": ", exc, sep="")

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
    cur.close()
    conn.close()

def main():
    # Require Python 3.12 or 3.13 to use the autocommit attribute.
    # assert sys.version_info >= (3, 12)
    if sys.version_info.major != 3 or sys.version_info.minor < 12:
        raise ValueError("This script requires Python >= 3.12.")
    args = parse_args()
    init_logging(args.log_level)
    save_data(args.csv_file, args.db_file, args.commit)

if __name__ == "__main__":
    main()
