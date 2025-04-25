"""
Database queries that return counts.
"""

from .. import db


def select_counts_by_year():
    """
    Return result set rows containing the year, the number of books acquired
    that year, and the number of books finished that year.
    """
    sql_select_year_counts = """
        SELECT
            x.year,
            y.books_acquired,
            x.books_finished
        FROM
            (
                SELECT
                    STRFTIME('%Y', tbl_note.finish_date) AS year,
                    COUNT(STRFTIME('%Y', tbl_note.finish_date)) as books_finished
                FROM
                    tbl_note
                WHERE
                    tbl_note.finish_date IS NOT NULL
                GROUP BY
                    STRFTIME('%Y', tbl_note.finish_date)

            ) AS x
            INNER JOIN
            (
                SELECT
                    STRFTIME('%Y', tbl_acquisition.acquisition_date) AS year,
                    COUNT(STRFTIME('%Y', tbl_acquisition.acquisition_date)) as books_acquired
                FROM
                    tbl_acquisition
                GROUP BY
                    STRFTIME('%Y', tbl_acquisition.acquisition_date)
            ) AS y
            ON x.year = y.year
    """
    cur = db.conn.execute(sql_select_year_counts)
    rows = cur.fetchall()
    cur.close()
    return rows


def select_total_books_acquired():
    """
    Return a result set row containing the total books acquired.
    """
    sql_select_total_books_acquired = """
        SELECT
            COUNT(tbl_acquisition.acquisition_date)
        FROM
            tbl_acquisition
    """
    cur = db.conn.execute(sql_select_total_books_acquired)
    row = cur.fetchone()
    cur.close()
    return row


def select_total_books_finished():
    """
    Return a result set row containing the total books finished.
    """
    sql_select_total_books_finished = """
        SELECT
            COUNT(tbl_note.finish_date)
        FROM
            tbl_note
        WHERE
            tbl_note.finish_date IS NOT NULL
    """
    cur = db.conn.execute(sql_select_total_books_finished)
    row = cur.fetchone()
    cur.close()
    return row


def select_total_books_unfinished():
    """
    Return a result set row containing the total books unfinished.
    """
    sql_select_total_books_unfinished = """
        SELECT
            COUNT(tbl_note.status_id)
        FROM
            tbl_note
            INNER JOIN tbl_status
                ON tbl_note.status_id = tbl_status.id
            INNER JOIN tbl_book
                ON tbl_note.book_id = tbl_book.id
        WHERE
            tbl_status.name = 'New'
            OR tbl_status.name = 'Started'
            AND tbl_book.id NOT IN (
                SELECT DISTINCT
                    tbl_book.id
                FROM
                    tbl_book
                    INNER JOIN tbl_note
                        ON tbl_book.id = tbl_note.book_id
                    INNER JOIN tbl_status
                        ON tbl_note.status_id = tbl_status.id
                WHERE
                    tbl_status.name = 'Finished'
            )
    """
    cur = db.conn.execute(sql_select_total_books_unfinished)
    row = cur.fetchone()
    cur.close()
    return row


def select_total_distinct_books_finished():
    """
    Return a result set row containing the total distinct books finished.
    Books finished more than once count once.
    """
    sql_select_total_distinct_books_finished = """
        SELECT
            COUNT(DISTINCT tbl_book.id) as books_finished
        FROM
            tbl_book
            INNER JOIN tbl_note
                ON tbl_book.id = tbl_note.book_id
        WHERE
            tbl_note.finish_date IS NOT NULL
    """
    cur = db.conn.execute(sql_select_total_distinct_books_finished)
    row = cur.fetchone()
    cur.close()
    return row
