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

##########

# Database code.


def connect():
    db_file = os.environ.get("SQLITE3_DB")
    conn = sqlite3.connect(database=db_file)
    sql_pragma_foreign_keys = "PRAGMA foreign_keys = ON"
    conn.execute(sql_pragma_foreign_keys)
    return conn


def select_acquisition_date(conn, book_id):
    sql_select_acquisition_date = """
        SELECT
            tbl_acquisition.acquisition_date
        FROM
            tbl_acquisition
        WHERE
            tbl_acquisition.book_id = ?
        LIMIT 1
    """
    cur = conn.execute(sql_select_acquisition_date, (book_id,))
    result_set = cur.fetchone()
    cur.close()
    return result_set[0]


def select_all_books(conn):
    sql_select_all_books = """
        SELECT
            tbl_book.title,
            tbl_book.book_pub_date,
            tbl_book.audio_pub_date,
            tbl_book.hours,
            tbl_book.minutes,
            tbl_book.id
        FROM
            tbl_book
    """
    cur = conn.execute(sql_select_all_books)
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_author_name(conn, author_id):
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
    author_name = result_set[0]
    return author_name


def select_authors_for_book(conn, book_id):
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
    cur = conn.execute(sql_select_authors_for_book, (book_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_books_for_author(conn, author_id):
    sql_select_books_for_author = """
        SELECT
            tbl_book.title,
            tbl_book.book_pub_date,
            tbl_book.audio_pub_date,
            tbl_book.hours,
            tbl_book.minutes,
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
    return result_set


def select_finished_dates(conn, book_id):
    sql_select_finished_dates = """
        SELECT DISTINCT
            tbl_note.finish_date,
            tbl_rating.stars || ' ' || tbl_rating.description AS rating 
        FROM
            tbl_note
            INNER JOIN tbl_rating
                ON tbl_note.rating_id = tbl_rating.id
        WHERE
            tbl_note.book_id = ?
            AND tbl_note.finish_date IS NOT NULL
            AND tbl_note.rating_id IS NOT NULL
        ORDER BY
            tbl_note.finish_date ASC
    """
    cur = conn.execute(sql_select_finished_dates, (book_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


############ HTML generation code.


def create_authors_td_html(conn, book_id, rowspan_attr):
    """
    Given a book_id, select the authors and format them with links in a
    td element. When there are multiple authors, use the first author as
    the sort key.
    """
    data_rows = select_authors_for_book(conn, book_id)
    author_strings = []
    first_author = True
    for row in data_rows:
        (author_id, author_name) = row
        if first_author:
            # Create a sorting key that starts with the author's last name.
            first_author_name_upper = author_name.upper()
            first_author_names = first_author_name_upper.split()
            first_author_names_key = " ".join([first_author_names[-1]] + first_author_names[:len(first_author_names) - 1])
            first_author = False
        author_string = f'<a class="adaptive" href="?author_id={author_id}">{author_name}</a>'
        author_strings.append(author_string)
    html = f'          <td data-author="{first_author_names_key}" class="adaptive"{rowspan_attr}>{", ".join(author_strings)}</td>\n'
    return html


def create_books_table_html(conn, books_result_set):
    """
    There can be multiple authors of a book, where each author will have a
    link in the table. The situation is identical for translators and
    narrators. The easiest way to deal with this is to use multiple
    queries.
    """
    html = '    <table class="adaptive">\n'
    html += '      <thead class="adaptive">\n'
    html += '        <tr class="adaptive">\n'
    for col_name in ["Title", "Authors", "Translators", "Narrators", "Book Publication Date", "Audiobook Publication Date", "Length"]:
        html += f'          <th class="adaptive">{col_name} <span>\u2195</span></th>\n'
    html += '        </tr>\n'
    html += '      </thead>\n'
    html += '      <tbody class="adaptive">\n'

    for row in books_result_set:
        (title, book_pub_date, audio_pub_date, hours, minutes, book_id) = row

        # Create keys for sorting by length or title.
        data_length = 60 * int(hours) + int(minutes)

        if title.startswith("A "):
            data_title = title[2:]
        elif title.startswith("An "):
            data_title = title[3:]
        elif title.startswith("The "):
            data_title = title[4:]
        else:
            data_title = title
        data_title = data_title.upper()
        
        # Convert hours and minutes to an hh:mm string.
        length = f"{hours}:{minutes:02d}"

        html += '        <tr class="adaptive">\n'
        html += f'          <td data-title="{data_title}" class="adaptive"><a class="adaptive" href="?book_id={book_id}">{title}</a></td>\n'
        html += create_authors_td_html(conn, book_id, "")
        html += '          <td class="adaptive"></td>\n' # translators
        html += '          <td class="adaptive"></td>\n' # narrators
        html += f'          <td class="adaptive">{book_pub_date if book_pub_date is not None else ""}</td>\n'
        html += f'          <td class="adaptive">{audio_pub_date if audio_pub_date is not None else ""}</td>\n'
        html += f'          <td data-length="{data_length}" class="adaptive right">{length}</td>\n'
        html += '        </tr>\n'
    html += '      </tbody>\n'
    html += '    </table>\n'
    return html


def create_end_html():
    end_html = """\
          </body>
        </html>"""
    return textwrap.dedent(end_html)


def create_finished_books_table_html(conn, books_result_set):
    """
    There can be multiple authors of a book, where each author will have a link
    in the table. A book can be finished more than once. The easiest way to deal
    with these is to use multiple queries.
    """
    th_tool_tip = "Click this header to sort the table by the values in this column."
    html = '    <table class="adaptive">\n'
    html += '      <thead class="adaptive">\n'
    html += '        <tr class="adaptive">\n'
    for col_name in ["Title", "Authors", "Length", "Acquired Date", "Finished Date", "Rating"]:
        html += f'          <th class="adaptive" title="{th_tool_tip}">{col_name} <span>\u2195</span></th>\n'
    html += '        </tr>\n'
    html += '      </thead>\n'
    html += '      <tbody class="adaptive">\n'

    # Sort the rows by the requested criterion since JavaScript can't sort the table correctly.
    for row in books_result_set:
        (title, book_pub_date, audio_pub_date, hours, minutes, book_id) = row

        # Create keys for sorting by length or title.
        data_length = 60 * int(hours) + int(minutes)

        # Create case-insensitive keys for sorting by title, ignoring "The", "A",
        # and "An" at the beginning of the title.
        if title.startswith("A "):
            data_title = title[2:]
        elif title.startswith("An "):
            data_title = title[3:]
        elif title.startswith("The "):
            data_title = title[4:]
        else:
            data_title = title
        data_title = data_title.upper()

        # Convert hours and minutes to an hh:mm string.
        length = f"{hours}:{minutes:02d}"

        # Select the acquisition date.
        acquisition_date = select_acquisition_date(conn, book_id)

        # Select the finished date and rating.
        rs = select_finished_dates(conn, book_id)

        # # Create table rows only for finished books, reporting all finished dates.
        # if len(rs) > 0:
        #     rowspan_count = len(rs)
        #     rowspan_attr = f' rowspan="{rowspan_count}"' if rowspan_count > 1 else ""
        #     html += '        <tr class="adaptive">\n'
        #     html += f'          <td data-title="{data_title}" class="adaptive"{rowspan_attr}><a class="adaptive" href="?book_id={book_id}">{title}</a></td>\n'
        #     html += create_authors_td_html(conn, book_id, rowspan_attr)
        #     html += f'          <td data-length="{data_minutes}" class="adaptive right"{rowspan_attr}>{length}</td>\n'
        #     html += f'          <td  class="adaptive"{rowspan_attr}>{acquisition_date}</td>\n'
        #     html += f'          <td class="adaptive">{rs[0][0]}</td>\n'
        #     html += f'          <td class="adaptive">{rs[0][1]}</td>\n'
        #     html += '        </tr>\n'

        #     for row in rs[1:]:
        #         html += '        <tr class="adaptive">\n'
        #         html += f'          <td class="adaptive">{row[0]}</td>\n'
        #         html += f'          <td class="adaptive">{row[1]}</td>\n'
        #         html += f'        </tr>\n'

        # Create table rows only for finished books, reporting only the first finished date.
        if len(rs) > 0:
            html += '        <tr class="adaptive">\n'
            html += f'          <td data-title="{data_title}" class="adaptive"><a class="adaptive" href="?book_id={book_id}">{title}</a></td>\n'
            html += create_authors_td_html(conn, book_id, "")
            html += f'          <td data-length="{data_length}" class="adaptive right">{length}</td>\n'
            html += f'          <td class="adaptive">{acquisition_date}</td>\n'
            html += f'          <td class="adaptive">{rs[0][0]}</td>\n'
            html += f'          <td class="adaptive">{rs[0][1]}</td>\n'
            html += '        </tr>\n'

    html += '      </tbody>\n'
    html += '    </table>\n'
    return html


def create_start_html():
    start_html = r"""        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Audiobooks</title>
            <link rel="stylesheet" href="styles.css">
            <script src="sort_table.js"></script>
          </head>
          <body>
        """
    return textwrap.dedent(start_html)


##########

# Display code.


def display_all_books(conn):
    print("Content-Type: text/html\r\n\r\n", end="")
    all_books_rs = select_all_books(conn)
    html = create_start_html()
    html += '    <h1 class="adaptive">All Audiobooks</h1>\n'
    html += create_books_table_html(conn, all_books_rs)
    html += create_end_html()
    print(html)


def display_finished_books(conn):
    """
        title, authors, length, acquisition_date, finish_date, rating
    """
    print("Content-Type: text/html\r\n\r\n", end="")
    all_books_rs = select_all_books(conn)
    html = create_start_html()
    html += '    <h1 class="adaptive">Finished Audiobooks</h1>\n'
    html += create_finished_books_table_html(conn, all_books_rs)
    html += create_end_html()
    print(html)


def display_author(conn, author_id):
    print("Content-Type: text/html\r\n\r\n", end="")
    html = create_start_html()
    author_name = select_author_name(conn, author_id)
    html += f'    <h1 class="adaptive">Audiobooks by {author_name}</h1>\n'
    books_for_author_rs = select_books_for_author(conn, author_id)
    html += create_books_table_html(conn, books_for_author_rs)
    html += create_end_html()
    print(html)


def display_book(conn, book_id):
    print("Content-Type: text/html\r\n\r\n", end="")
    html = create_start_html()
    html += f'    <h1 class="adaptive">Book {book_id}</h1>'
    html += f'    <p class="adaptive">{book_id}</p>'
    html += create_end_html()
    print(html)


def main():
    conn = connect()
    fs = cgi.FieldStorage()
    if "author_id" in fs:
        display_author(conn, fs["author_id"].value)
    elif "book_id" in fs:
        display_book(conn, fs["book_id"].value)
    else:
        display_finished_books(conn)
    conn.close()


if __name__ == "__main__":
    main()
