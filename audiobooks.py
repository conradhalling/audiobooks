"""
Manage database interactions.

This code is intended to be database-agnostic, but there are specific methods
for the sqlite3 database. The sqlalchemy.Engine object is passed to methods
in this module.
"""
import os

import sqlalchemy


def create_tables(engine):
    metadata = sqlalchemy.MetaData()
    tbl_read_status = sqlalchemy.Table(
        "tbl_read_status",
        metadata,
        sqlalchemy.Column(
            "id",
            sqlalchemy.Integer(),
            nullable=False,
            primary_key=True,
        ),
        sqlalchemy.Column(
            "name",
            sqlalchemy.Text(),
            nullable=False,
        ),
        sqlalchemy.Column(
            "description",
            sqlalchemy.Text(),
            nullable=False,
        ),
    )

    tbl_purchase_type = sqlalchemy.Table(
        "tbl_purchase_type",
        metadata,
        sqlalchemy.Column(
            "id",
            sqlalchemy.Integer(),
            nullable=False,
            primary_key=True,
        ),
        sqlalchemy.Column(
            "name",
            sqlalchemy.Text(),
            nullable=False,
        ),
        sqlalchemy.Column(
            "description",
            sqlalchemy.Text(),
            nullable=False,
        ),
    )

    tbl_author = sqlalchemy.Table(
        "tbl_author",
        metadata,
        sqlalchemy.Column(
            "id",
            sqlalchemy.Integer(),
            nullable=False,
            primary_key=True,
        ),
        sqlalchemy.Column(
            "last_name",
            sqlalchemy.Text(),
            nullable=False,
        ),
        sqlalchemy.Column(
            "first_name",
            sqlalchemy.Text(),
            nullable=True,
        ),
        sqlalchemy.Column(
            "middle_names",
            sqlalchemy.Text(),
            nullable=True,
        ),
    )

    tbl_book = sqlalchemy.Table(
        "tbl_book",
        metadata,
        sqlalchemy.Column(
            "id",
            sqlalchemy.Integer(),
            nullable=False,
            primary_key=True,
        ),
        sqlalchemy.Column(
            "title",
            sqlalchemy.Text(),
            nullable=False,
        ),
        sqlalchemy.Column(
            "length_hours",
            sqlalchemy.Integer(),
            sqlalchemy.CheckConstraint("length_hours >= 0"),
            nullable=False,
        ),
        sqlalchemy.Column(
            "length_minutes",
            sqlalchemy.Integer(),
            sqlalchemy.CheckConstraint("length_minutes >= 0 and length_minutes < 60"),
            nullable=False,
        ),
        sqlalchemy.Column(
            "read_status_id",
            sqlalchemy.Integer(),
            sqlalchemy.ForeignKey("tbl_read_status.id"),
            nullable=False,
        ),
        sqlalchemy.Column(
            "purchase_type_id",
            sqlalchemy.Integer(),
            sqlalchemy.ForeignKey("tbl_purchase_type.id"),
            nullable=False,
        ),
        sqlalchemy.Column(
            "purchase_date",
            sqlalchemy.Date(),
            nullable=False,
        ),
        sqlalchemy.Column(
            "credit",
            sqlalchemy.Integer(),
            nullable=True,
        ),
        sqlalchemy.Column(
            "price",
            sqlalchemy.Numeric(),
            nullable=True,
        ),
        sqlalchemy.Column(
            "available",
            sqlalchemy.Boolean(),
            nullable=False,
            default=True,
        ),
    )

    tbl_book_author = sqlalchemy.Table(
        "tbl_book_author",
        metadata,
        sqlalchemy.Column(
            "id",
            sqlalchemy.Integer(),
            nullable=False,
            primary_key=True,
        ),
        sqlalchemy.Column(
            "book_id",
            sqlalchemy.Integer(),
            sqlalchemy.ForeignKey("tbl_book.id"),
            nullable=False,
        ),
        sqlalchemy.Column(
            "author_id",
            sqlalchemy.Integer(),
            sqlalchemy.ForeignKey("tbl_author.id"),
            nullable=False,
        ),
    )

    tbl_book_finished = sqlalchemy.Table(
        "tbl_book_finished",
        metadata,
        sqlalchemy.Column(
            "id",
            sqlalchemy.Integer(),
            nullable=False,
            primary_key=True,
        ),
        sqlalchemy.Column(
            "book_id",
            sqlalchemy.Integer(),
            sqlalchemy.ForeignKey("tbl_book.id"),
            nullable=False,
        ),
        sqlalchemy.Column(
            "finished_date",
            sqlalchemy.Date(),
            nullable=False,
        ),
        sqlalchemy.Column(
            "rating",
            sqlalchemy.Integer(),
            sqlalchemy.CheckConstraint("rating >= 1 and rating <= 5"),
            nullable=False,
        ),
        sqlalchemy.Column(
            "comments",
            sqlalchemy.Text(),
            nullable=False,
        ),
    )

    metadata.create_all(engine)
    load_tbl_purchase_type(engine)


def init_sqlite():
    """
    Enforce foreign key constraints on every connection.
    See https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support.
    """

    @sqlalchemy.event.listens_for(sqlalchemy.engine.Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# This code checks to see if sqlite3 is being used:
# from sqlalchemy import event
# from sqlalchemy.engine import Engine
# from sqlite3 import Connection as SQLite3Connection

# @event.listens_for(Engine, "connect")
# def _set_sqlite_pragma(dbapi_connection, connection_record):
#     if isinstance(dbapi_connection, SQLite3Connection):
#         cursor = dbapi_connection.cursor()
#         cursor.execute("PRAGMA foreign_keys=ON;")
#         cursor.close()


def insert_data(engine, df):
    """
    Insert the data from the pandas DataFrame into the database tables.

    The algorithm is complex.
    """
    # Get table objects from the engine.
    metadata = sqlalchemy.MetaData()
    metadata.reflect(engine)
    tbl_author = metadata.tables["tbl_author"]
    tbl_book = metadata.tables["tbl_book"]
    tbl_book_author = metadata.tables["tbl_book_author"]
    tbl_book_finished = metadata.tables["tbl_book_finished"]
    tbl_purchase_type = metadata.tables["tbl_purchase_type"]
    tbl_read_status = metadata.tables["tbl_read_status"]

    with engine.connect() as conn02:
        for i, row in df.iterrows():
            title = row["Title"]
            authors = row["Author"]
            length_hours = row["Hours"]
            length_minutes = row["Minutes"]
            purchase_date = row["Purchased Date"]
            read_status = row["Status"]
            finish_date = row["Finished Date"]
            purchase_type_txt = row["Purchase Type"]
            credits = row["Credits"]
            price = row["Price"]
            rating = row["Rating"]
            notes = row["Notes"]

            try:
                # If the book already exists, don't insert it.
                # Check that all fields match; if not, there is a DataError exception.

                # If an ID doesn't already exist for the book's title, the book is new.

                # Split the Authors field on ";".
                # Look up each author and get the author's ID.
                # Insert any new author and get the author's ID.

                # Look up the book and get the book's ID.
                # This is not straight-forward since two books by different authors
                # may have the same title.

                # Link the book and its authors.
                conn02.commit()
            except Exception as exc:
                conn02.rollback()
                print(exc)


def load_tbl_purchase_type(engine):
    """
    Insert the standard values into tbl_purchase_type.
    """
    metadata = sqlalchemy.MetaData()
    metadata.reflect(engine)
    tbl_purchase_type = metadata.tables["tbl_purchase_type"]
    stmt01 = sqlalchemy.insert(tbl_purchase_type)
    values_list01 = [
        {"name": "credit", "description": "Purchased with an audible credit."},
        {"name": "extra", "description": "Purchased with money."},
        {"name": "free", "description": "Free book."},
        {"name": "plus", "description": "Free book from the Plus catalog."},
    ]
    with engine.begin() as conn01:
        result_proxy01 = conn01.execute(stmt01, values_list01)
        print(
            "Inserted {} rows into tbl_purchase_type.".format(result_proxy01.rowcount)
        )


def remove_sqlite3_file(sqlite3_filepath):
    try:
        os.remove(sqlite3_filepath)
        print("File {} removed.".format(sqlite3_filepath))
    except FileNotFoundError as esc:
        print("File {} not found.".format(sqlite3_filepath))
