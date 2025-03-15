"""
db is a wrapper for connecting to the database, managing transactions,
and interacting with the database.

Make all modules availabe on import of the package.

The database connection is stored in db.conn.conn.
"""

import logging
logger = logging.getLogger(__name__)
import sqlite3

from . import acquisition_type
from . import author
from . import book
from . import conn
from . import db
from . import narrator
from . import rating
from . import translator
from . import vendor


# Functions are listed in alphabetical order.

def begin_transaction():
    conn.conn.execute("BEGIN TRANSACTION")


def close():
    conn.conn.close()
    conn.conn = None


def commit():
    conn.conn.execute("COMMIT")


def connect(db_file):
    conn.conn = sqlite3.connect(database=db_file, isolation_level=None)


def create_tables():
    author.create_table()
    narrator.create_table()
    translator.create_table()
    vendor.create_table()
    book.create_table()
    db.create_tbl_book_author(conn.conn)
    db.create_tbl_book_narrator(conn.conn)
    db.create_tbl_book_translator(conn.conn)
    db.create_tbl_book_vendor(conn.conn)
    acquisition_type.create_table()
    rating.create_table()


def enforce_foreign_key_constraints():
    """
    Set PRAGMA foreign_keys = ON.
    """
    cur = conn.conn.cursor()
    # Set the pragma.
    if conn.conn.in_transaction == True:
        # This is needed when conn.autocommit is False because a transaction
        # is already open, and PRAGMA foreign_keys = ON has no effect in
        # an open transaction.
        cur.executescript("COMMIT; PRAGMA foreign_keys = ON; BEGIN;")
    else:
        cur.execute("PRAGMA foreign_keys = ON")
    cur.close()
    verify_foreign_key_constraints()


def rollback():
    conn.conn.execute("ROLLBACK")


def verify_foreign_key_constraints():
    """
    Verify that the PRAGMA foreign_keys value is 1.
    Raise a sqlite3.IntegrityError exception if the value is not 1.
    """
    # Get the pragma. It must be 1.
    cur = conn.conn.cursor()
    cur.execute("PRAGMA foreign_keys")
    rows = cur.fetchall()
    cur.close()
    pragma_foreign_keys_value = None
    if len(rows) != 0:
        pragma_foreign_keys_value = rows[0][0]
    logger.debug(f"pragma_foreign_keys_value: {pragma_foreign_keys_value}")
    if pragma_foreign_keys_value != 1:
        raise sqlite3.IntegrityError("PRAGMA foreign_keys is not ON")
