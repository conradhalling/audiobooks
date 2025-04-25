"""
db is a wrapper for connecting to the database, managing transactions,
and interacting with the database.

Make all modules available on import of the package.

The database connection is stored in db.conn.
"""

import logging
logger = logging.getLogger(__name__)
import sqlite3

from . import acquisition
from . import acquisition_type
from . import author
from . import book
from . import book_author
from . import book_narrator
from . import book_translator
from . import counts
from . import narrator
from . import note
from . import rating
from . import status
from . import translator
from . import user
from . import vendor

# db.conn is a singleton containing the connection to the SQLite database file.
conn = None

# Functions are listed in alphabetical order.

def begin_transaction():
    global conn
    conn.execute("BEGIN TRANSACTION")


def close():
    global conn
    if conn is not None:
        conn.close()
        conn = None


def commit():
    global conn
    conn.execute("COMMIT")


def connect(db_file):
    global conn
    conn = sqlite3.connect(database=db_file, isolation_level=None)
    enforce_foreign_key_constraints()


def create_schema():
    user.create_table()
    author.create_table()
    narrator.create_table()
    translator.create_table()
    vendor.create_table()
    book.create_table()
    status.create_table()
    note.create_table()
    acquisition_type.create_table()
    rating.create_table()
    book_author.create_table()
    book_narrator.create_table()
    book_translator.create_table()
    acquisition.create_table()


def enforce_foreign_key_constraints():
    """
    Set PRAGMA foreign_keys = ON.
    """
    global conn
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
    verify_foreign_key_constraints()


def rollback():
    global conn
    conn.execute("ROLLBACK")


def verify_foreign_key_constraints():
    """
    Verify that the PRAGMA foreign_keys value is 1.
    Raise a sqlite3.IntegrityError exception if the value is not 1.
    """
    # Get the pragma. It must be 1.
    global conn
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
