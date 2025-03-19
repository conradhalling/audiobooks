#!/Users/halto/src/conradhalling/audiobooks/venv310/bin/python3

"""
This script does not use the db package (yet).
"""

import cgi
import cgitb
cgitb.enable()
import os
import sqlite3
import textwrap

from dotenv import load_dotenv
load_dotenv()


def select_all_books():
    db_file = os.environ.get("SQLITE3_DB")
    conn = sqlite3.connect(database=db_file)
    sql_pragma_foreign_keys = "PRAGMA foreign_keys = ON"
    conn.execute(sql_pragma_foreign_keys)

    sql_select_all_books = """
        SELECT
            tbl_book.title,
            tbl_book.book_pub_date,
            tbl_book.audio_pub_date,
            tbl_book.hours || ':' || format('%02d', tbl_book.minutes) AS book_length,
            tbl_book.id
        FROM
            tbl_book
    """
    cur = conn.execute(sql_select_all_books)
    result_set = cur.fetchall()
    cur.close()
    conn.close()
    return result_set


def select_books_for_author(author_id):
    db_file = os.environ.get("SQLITE3_DB")
    conn = sqlite3.connect(database=db_file)
    sql_pragma_foreign_keys = "PRAGMA foreign_keys = ON"
    conn.execute(sql_pragma_foreign_keys)

    sql_select_books_for_author = """
        SELECT
            tbl_book.title,
            tbl_book.book_pub_date,
            tbl_book.audio_pub_date,
            tbl_book.hours || ':' || format('%02d', tbl_book.minutes) AS book_length,
            tbl_book.id
        FROM
            tbl_book
            INNER JOIN tbl_book_author
                ON tbl_book.id = tbl_book_author.book_id
        WHERE
            tbl_book_author.author_id = ?
    """
    cur = conn.execute(sql_select_books_for_author, (author_id,))
    result_set = cur.fetchall()
    cur.close()
    conn.close()
    return result_set


def select_author_name(author_id):
    db_file = os.environ.get("SQLITE3_DB")
    conn = sqlite3.connect(database=db_file)
    sql_pragma_foreign_keys = "PRAGMA foreign_keys = ON"
    conn.execute(sql_pragma_foreign_keys)

    sql_select_author = """
        SELECT
            tbl_author.name
        FROM
            tbl_author
        WHERE
            tbl_author.id = ?
    """
    cur = conn.execute(sql_select_author, (author_id,))
    result_set = cur.fetchone()
    cur.close()
    conn.close()
    author_name = result_set[0]
    return author_name


def create_start_html():
    start_html = """\
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Audiobooks</title>
            <link rel="stylesheet" href="styles.css">
          </head>
          <body>"""
    return textwrap.dedent(start_html)


def create_end_html():
    end_html = """\
          </body>
        </html>"""
    return textwrap.dedent(end_html)


def create_books_table_html(books_result_set):
    """
    There can be multiple authors of a book, where each author will have a
    link in the table. The situation is identical for translators and
    narrators. The easiest way to deal with this is to use multiple
    queries.
    """
    html = ""
    html += '    <table class="adaptive">\n'
    html += '      <thead class="adaptive">\n'
    html += '        <tr class="adaptive">\n'
    for col_name in ["Title", "Authors", "Translators", "Narrators", "Book Publication Date", "Audiobook Publication Date", "Length"]:
        html += f'          <th class="adaptive">{col_name}</th>\n'
    html += '        </tr>\n'
    html += '      </thead>\n'
    html += '      <tbody class="adaptive">\n'

    for row in books_result_set:
        (title, book_pub_date, audio_pub_date, length, book_id) = row
        html += '        <tr class="adaptive">\n'
        html += f'          <td class="adaptive"><a class="adaptive" href="?book_id={book_id}">{title}</a></td>\n'
        html += create_authors_td_html(book_id)
        html += '          <td class="adaptive"></td>\n' # translators
        html += '          <td class="adaptive"></td>\n' # narrators
        html += f'          <td class="adaptive">{book_pub_date if book_pub_date is not None else ""}</td>\n'
        html += f'          <td class="adaptive">{audio_pub_date if audio_pub_date is not None else ""}</td>\n'
        html += f'          <td class="adaptive right">{length}</td>\n'
        html += '        </tr>\n'
    html += '      </tbody>\n'
    html += '    </table>\n'
    return html


def create_authors_td_html(book_id):
    """
    Given a book_id, select the authors and format them with links in a
    td element.
    """
    data_rows = select_authors_for_book(book_id)
    author_strings = []
    for row in data_rows:
        (author_id, author_name) = row
        author_string = f'<a class="adaptive" href="?author_id={author_id}">{author_name}</a>'
        author_strings.append(author_string)
    html = f'          <td class="adaptive">{" & ".join(author_strings)}</td>\n'
    return html


def select_authors_for_book(book_id):
    sql_select_authors_for_book = """
        SELECT
            tbl_author.id,
            tbl_author.name
        FROM
            tbl_book_author
            INNER JOIN tbl_author
                ON tbl_book_author.author_id = tbl_author.id
        WHERE
            tbl_book_author.book_id = ?
    """
    db_file = os.environ.get("SQLITE3_DB")
    conn = sqlite3.connect(database=db_file)
    sql_pragma_foreign_keys = "PRAGMA foreign_keys = ON"
    conn.execute(sql_pragma_foreign_keys)
    cur = conn.execute(sql_select_authors_for_book, (book_id,))
    result_set = cur.fetchall()
    cur.close()
    conn.close()
    return result_set


def display_all_books():
    all_books_rs = select_all_books()
    html = create_start_html()
    html += '    <h1 class="adaptive">All Audiobooks</h1>\n'
    html += create_books_table_html(all_books_rs)
    html += create_end_html()
    print(html)


def display_author(author_id):
    html = create_start_html()
    author_name = select_author_name(author_id)
    html += f'    <h1 class="adaptive">Audiobooks by {author_name}</h1>\n'
    books_for_author_rs = select_books_for_author(author_id)
    html += create_books_table_html(books_for_author_rs)
    html += create_end_html()
    print(html)


def display_book(book_id):
    create_start_html()
    print(f'    <h1 class="adaptive">Book {book_id}</h1>')
    print(f'    <p class="adaptive">{book_id}</p>')
    create_end_html()


def main():
    print("Content-Type: text/html\r\n\r\n", end="")
    fs = cgi.FieldStorage()
    if "author_id" in fs:
        display_author(fs["author_id"].value)
    elif "book_id" in fs:
        display_book(fs["book_id"].value)
    else:
        display_all_books()


if __name__ == "__main__":
    main()
