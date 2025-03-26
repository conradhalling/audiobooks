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


def select_acquisition_for_book(conn, book_id):
    sql_select_acquisition_for_book = """
        SELECT
            tbl_user.username,
            tbl_acquisition.id,
            tbl_vendor.name,
            tbl_acquisition_type.name,
            tbl_acquisition.acquisition_date,
            tbl_acquisition.discontinued,
            tbl_acquisition.audible_credits,
            tbl_acquisition.price_in_cents
        FROM
            tbl_acquisition
            INNER JOIN tbl_user
                ON tbl_acquisition.user_id = tbl_user.id
            INNER JOIN tbl_vendor
                ON tbl_acquisition.vendor_id = tbl_vendor.id
            INNER JOIN tbl_acquisition_type
                ON tbl_acquisition.acquisition_type_id = tbl_acquisition_type.id
        WHERE
            tbl_acquisition.book_id = ?
    """
    cur = conn.execute(sql_select_acquisition_for_book, (book_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


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
            INNER JOIN tbl_acquisition
                ON tbl_book.id = tbl_acquisition.book_id
        ORDER BY
            tbl_acquisition.acquisition_date DESC,
            tbl_book.title ASC
    """
    cur = conn.execute(sql_select_all_books)
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_author_name(conn, author_id):
    sql_select_author = """
        SELECT
            tbl_author.surname,
            tbl_author.forename
        FROM
            tbl_author
        WHERE
            tbl_author.id = ?
    """
    cur = conn.execute(sql_select_author, (author_id,))
    result_set = cur.fetchone()
    cur.close()
    author_name = result_set[1] + " " + result_set[0]
    return author_name


def select_authors_for_book(conn, book_id):
    sql_select_authors_for_book = """
        SELECT
            tbl_author.id,
            tbl_author.surname,
            tbl_author.forename
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


def select_book(conn, book_id):
    sql_select_book = """
        SELECT
            tbl_book.id,
            tbl_book.title,
            tbl_book.book_pub_date,
            tbl_book.audio_pub_date,
            tbl_book.hours,
            tbl_book.minutes
        FROM
            tbl_book
        WHERE
            tbl_book.id = ?
    """
    cur = conn.execute(sql_select_book, (book_id,))
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
            INNER JOIN tbl_status
                ON tbl_note.status_id = tbl_status.id
                AND tbl_status.name = 'Finished'
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


def select_narrators_for_book(conn, book_id):
    sql_select_narrators_for_book = """
        SELECT
            tbl_narrator.id,
            tbl_narrator.name
        FROM
            tbl_book_narrator
            INNER JOIN tbl_narrator
                ON tbl_book_narrator.narrator_id = tbl_narrator.id
        WHERE
            tbl_book_narrator.book_id = ?
    """
    cur = conn.execute(sql_select_narrators_for_book, (book_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_notes_for_book(conn, book_id):
    sql_select_notes_for_book = """
        SELECT
            tbl_user.username,
            tbl_status.name AS status_name,
            tbl_note.finish_date,
            tbl_rating.stars,
            tbl_rating.description,
            tbl_note.comments
        FROM
            tbl_note
            INNER JOIN tbl_user
                ON tbl_note.user_id = tbl_user.id
            LEFT OUTER JOIN tbl_status
                ON tbl_note.status_id = tbl_status.id
            LEFT OUTER JOIN tbl_rating
                ON tbl_note.rating_id = tbl_rating.id
        WHERE
            tbl_note.book_id = ?
        ORDER BY
            tbl_note.finish_date
    """
    cur = conn.execute(sql_select_notes_for_book, (book_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_translators_for_book(conn, book_id):
    sql_select_translators_for_book = """
        SELECT
            tbl_translator.id,
            tbl_translator.name
        FROM
            tbl_book_translator
            INNER JOIN tbl_translator
                ON tbl_book_translator.translator_id = tbl_translator.id
        WHERE
            tbl_book_translator.book_id = ?
    """
    cur = conn.execute(sql_select_translators_for_book, (book_id,))
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
        (author_id, author_surname, author_forename) = row
        # author_surname can be None.
        if author_surname is None:
            author_name = author_forename
        else:
            author_name = author_forename + " " + author_surname
        if first_author:
            # Create a sorting key that starts with the author's last name.
            if author_surname is None:
                sort_key_author_name = author_forename
            else:
                sort_key_author_name = author_surname + " " + author_forename
            sort_key_author_name = sort_key_author_name.upper()
            first_author = False
        author_string = f'<a href="?author_id={author_id}">{author_name}</a>'
        author_strings.append(author_string)
    html = f'          <td data-sortkey="{sort_key_author_name}"{rowspan_attr}>{", ".join(author_strings)}</td>\n'
    return html


def create_books_table_html(conn, books_result_set):
    """
    There can be multiple authors of a book, where each author will have a
    link in the table. The situation is identical for translators and
    narrators. The easiest way to deal with this is to use multiple
    queries.
    """
    html = '    <table>\n'
    html += '      <thead>\n'
    html += '        <tr>\n'
    for col_name in ["Title", "Authors", "Translators", "Narrators", "Book Publication Date", "Audiobook Publication Date", "Length"]:
        html += f'          <th class="sortable">{col_name} <span>⭥</span></th>\n'
    html += '        </tr>\n'
    html += '      </thead>\n'
    html += '      <tbody>\n'

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

        html += '        <tr>\n'
        html += f'          <td data-sortkey="{data_title}"><a href="?book_id={book_id}">{title}</a></td>\n'
        html += create_authors_td_html(conn, book_id, "")
        html += '          <td></td>\n' # translators
        html += '          <td></td>\n' # narrators
        html += f'          <td>{book_pub_date if book_pub_date is not None else ""}</td>\n'
        html += f'          <td>{audio_pub_date if audio_pub_date is not None else ""}</td>\n'
        html += f'          <td data-sortkey="{data_length}" class="right">{length}</td>\n'
        html += '        </tr>\n'
    html += '      </tbody>\n'
    html += '    </table>\n'
    return html


def create_end_html():
    end_html = """\
            </main>
          </body>
        </html>"""
    return textwrap.dedent(end_html)


def create_finished_books_table_html(conn, books_result_set):
    """
    This is actually *all* books, now.
    
    "⭥" is "\u2B65" or "&#x2B65;".
    """
    th_tool_tip = "Click this header to sort the table by the values in this column."
    html = '    <div class="table-filtered">'
    html += '    <strong>Status Filter:</strong>\n'
    html += '    <input type="checkbox" id="new" title="Click this checkbox to toggle the visibility of new audiobooks." checked>\n'
    html += '    <label for="new" title="Click this checkbox to toggle the visibility of new audiobooks.">New</label>\n'
    html += '    <input type="checkbox" id="started" title="Click this checkbox to toggle the visibility of started audiobooks." checked>\n'
    html += '    <label for="started" title="Click this checkbox to toggle the visibility of started audiobooks.">Started</label>\n'
    html += '    <input type="checkbox" id="finished" title="Click this checkbox to toggle the visibility of finished audiobooks." checked>\n'
    html += '    <label for="finished" title="Click this checkbox to toggle the visibility of finished audiobooks.">Finished</label>\n'

    html += '    <table id="books">\n'
    html += '      <thead>\n'
    html += '        <tr>\n'
    for col_name in ["Title", "Authors", "Length", "Acquisition Date", "Status", "Finished Date", "Rating"]:
        html += f'          <th class="sortable" title="{th_tool_tip}">{col_name} <span>⭥</span></th>\n'
    html += '        </tr>\n'
    html += '      </thead>\n'
    html += '      <tbody>\n'

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

        # Select the status, finished date (may be null), rating stars (may
        # be null), and rating description. Create strings for the HTML output.
        rs = select_notes_for_book(conn, book_id)
        status = rs[0][1]
        finish_date = rs[0][2]
        rating_stars = rs[0][3]
        rating_description = rs[0][4]
        rating = ""
        if finish_date is None:
            finish_date = ""
        if rating_stars is not None:
            rating = str(rating_stars) + " " + rating_description

        # Create table rows for all books, reporting only the first finished date.
        if len(rs) > 0:
            html += f'        <tr class="{status.lower()}">\n'
            html += f'          <td data-sortkey="{data_title}"><a href="?book_id={book_id}">{title}</a></td>\n'
            html += create_authors_td_html(conn, book_id, "")
            html += f'          <td data-sortkey="{data_length}" class="right">{length}</td>\n'
            html += f'          <td>{acquisition_date}</td>\n'
            html += f'          <td>{status}</td>\n'
            html += f'          <td>{finish_date}</td>\n'
            html += f'          <td>{rating}</td>\n'
            html += '        </tr>\n'

    html += '      </tbody>\n'
    html += '    </table>\n'
    html += '    </div>\n'
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
            <header>
              <nav>
                <ul>
                  <li class="logo"><a href="index.cgi">🎧<em>Audio</em>books📚</a></li>
                  <li><a href="index.cgi">Audiobooks</a></li>
                  <li><a href="#">Authors</a></li>
                  <li><a href="#">Narrators</a></li>
                  <li><a href="#">About</a></li>
                  <li><a href="#">Log In</a></li>
                  <li class="blog"><a href="/blog/">Blog</a></li>
                </ul>
              </nav>
            </header>
            <main style="margin-top: 50px">
        """
    return textwrap.dedent(start_html)


##########

# Get data code.

def get_book_data(conn, book_id):
    book_rs = select_book(conn, book_id)
    if book_rs is None:
        raise ValueError(f"Found no information for book ID {book_id}.")
    (db_book_id, title, book_pub_date, audio_pub_date, hours, minutes,) = book_rs[0]
    book_dict = {
        "book_id": db_book_id,
        "title": title,
        "book_pub_date": book_pub_date,
        "audio_pub_date": audio_pub_date,
        "hours": hours,
        "minutes": minutes,
    }

    authors_rs = select_authors_for_book(conn, book_id)
    authors_list = []
    for row in authors_rs:
        (author_id, author_surname, author_forename) = row
        author_dict = {
            "author_id": author_id,
            "author_surname": author_surname,
            "author_forename": author_forename,
        }
        authors_list.append(author_dict)
    book_dict["authors"] = authors_list

    translators_rs = select_translators_for_book(conn, book_id)
    translators_list = []
    for row in translators_rs:
        (translator_id, translator_name) = row
        translator_dict = {
            "translator_id": translator_id,
            "translator_name": translator_name,
        }
        translators_list.append(translator_dict)
    book_dict["translators"] = translators_list

    narrators_rs = select_narrators_for_book(conn, book_id)
    narrators_list = []
    for row in narrators_rs:
        (narrator_id, narrator_name) = row
        narrator_dict = {
            "narrator_id": narrator_id,
            "narrator_name": narrator_name,
        }
        narrators_list.append(narrator_dict)
    book_dict["narrators"] = narrators_list

    acquisition_rs = select_acquisition_for_book(conn, book_id)
    row = acquisition_rs[0]
    (username, acquisition_id, vendor_name, acquisition_type, acquisition_date,
     discontinued, audible_credits, price_in_cents) = row
    acquisition_dict = {
        "username": username,
        "acquisition_id": acquisition_id,
        "vendor_name": vendor_name,
        "acquisition_type": acquisition_type,
        "acquisition_date": acquisition_date,
        "discontinued": discontinued,
        "audible_credits": audible_credits,
        "price_in_cents": price_in_cents,
    }
    book_dict["acquisition"] = acquisition_dict

    notes_rs = select_notes_for_book(conn, book_id)
    notes_list = []
    for row in notes_rs:
        (username, status, finish_date, rating_stars, rating_description, comments) = row
        note_dict = {
            "username": username,
            "status": status,
            "finish_date": finish_date,
            "rating_stars": rating_stars,
            "rating_description": rating_description,
            "comments": comments,
        }
        notes_list.append(note_dict)
    book_dict["notes"] = notes_list

    return book_dict


##########


# Display code.


def display_all_books(conn):
    print("Content-Type: text/html\r\n\r\n", end="")
    all_books_rs = select_all_books(conn)
    html = create_start_html()
    html += '    <h1>All Audiobooks</h1>\n'
    html += create_books_table_html(conn, all_books_rs)
    html += create_end_html()
    print(html)


def display_author(conn, author_id):
    print("Content-Type: text/html\r\n\r\n", end="")
    html = create_start_html()
    author_name = select_author_name(conn, author_id)
    html += f'    <h1>Audiobooks by {author_name}</h1>\n'
    books_for_author_rs = select_books_for_author(conn, author_id)
    html += create_books_table_html(conn, books_for_author_rs)
    html += create_end_html()
    print(html)


def display_book(conn, book_id):
    print("Content-Type: text/html\r\n\r\n", end="")
    html = create_start_html()
    book = get_book_data(conn, book_id)
    
    # Precompute cell values.
    length = "" if book["hours"] is None else f'{book["hours"]}:{book["minutes"]:02d}'
    book_pub_date = "" if book["book_pub_date"] is None else book["book_pub_date"]
    audio_pub_date = "" if book["audio_pub_date"] is None else book["audio_pub_date"]
    price_in_dollars = "" if book["acquisition"]["price_in_cents"] is None\
        else "$" + str(float(book["acquisition"]["price_in_cents"] / 100))
    discontinued = "" if book["acquisition"]["discontinued"] is None else "discontinued"
    
    author_strings = []
    author_html_strings = []
    for author_dict in book["authors"]:
        author_id = author_dict["author_id"]
        author_surname = author_dict["author_surname"]
        author_forename = author_dict["author_forename"]
        author_name = f"{author_forename} {author_surname}"
        author_html_string = f'<a href="?author_id={author_id}">{author_name}</a>'
        author_html_strings.append(author_html_string)
        author_strings.append(author_name)
    
    translator_html_strings = []
    for translator_dict in book["translators"]:
        translator_id = translator_dict["translator_id"]
        translator_name = translator_dict["translator_name"]
        translator_string = f'<a href="?translator_id={translator_id}">{translator_name}</a>'
        translator_html_strings.append(translator_string)

    narrator_html_strings = []
    for narrator_dict in book["narrators"]:
        narrator_id = narrator_dict["narrator_id"]
        narrator_name = narrator_dict["narrator_name"]
        narrator_string = f'<a href="?narrator_id={narrator_id}">{narrator_name}</a>'
        narrator_html_strings.append(narrator_string)

    html += f'    <h1><cite>{book["title"]}</cite>, by {", ".join(author_strings)}</h1>'
    html += '    <h2>Book Information</h2>\n'
    html += '    <table>\n'
    html += '      <tbody class="vertical">\n'

    # Title
    html += '        <tr>\n'
    html += '          <th class="vertical">Title</th>\n'
    html += f'          <td><cite>{book["title"]}</cite></td>\n'
    html += '        </tr>\n'

    # Authors
    html += '        <tr>\n'
    html += '          <th class="vertical">Author{}</th>\n'.format(
        "s" if len(author_strings) > 1 else "")
    html += f'          <td>{", ".join(author_html_strings)}</td>\n'
    html += '        </tr>\n'

    # Length
    html += '        <tr>\n'
    html += '          <th class="vertical">Length (hr:min)</th>\n'
    html += f'          <td>{length}</td>\n'
    html += '        </tr>\n'

    # Translators
    if len(translator_html_strings) > 0:
        html += '        <tr>\n'
        html += '          <th class="vertical">Translator{}</th>\n'.format(
            "s" if len(translator_html_strings) > 1 else "")
        html += f'          <td>{", ".join(translator_html_strings)}</td>\n'
        html += '        </tr>\n'

    # Narrators
    html += '        <tr>\n'
    html += '          <th class="vertical">Narrator{}</th>\n'.format(
        "s" if len(narrator_html_strings) != 1 else "")
    html += f'          <td>{", ".join(narrator_html_strings)}</td>\n'
    html += '        </tr>\n'

    # Book Pub. Date
    if book_pub_date:
        html += '        <tr>\n'
        html += '          <th class="vertical">Book Pub. Date</th>\n'
        html += f'          <td>{book_pub_date}</td>\n'
        html += '        </tr>\n'

    # Audio Pub. Date
    if audio_pub_date:
        html += '        <tr>\n'
        html += '          <th class="vertical">Audio Pub. Date</th>\n'
        html += f'          <td>{audio_pub_date}</td>\n'
        html += '        </tr>\n'

    # Acquired By
    html += '        <tr>\n'
    html += '          <th class="vertical">Acquired By</th>\n'
    html += f'          <td>{book["acquisition"]["username"]}</td>\n'
    html += '        </tr>\n'

    # Vendor
    html += '        <tr>\n'
    html += '          <th class="vertical">Vendor</th>\n'
    html += f'          <td>{book["acquisition"]["vendor_name"]}</td>\n'
    html += '        </tr>\n'

    # Acquisition Type
    html += '        <tr>\n'
    html += '          <th class="vertical">Acquisition Type</th>\n'
    html += f'          <td>{book["acquisition"]["acquisition_type"]}</td>\n'
    html += '        </tr>\n'

    # Acquisition Date
    html += '        <tr>\n'
    html += '          <th class="vertical">Acquisition Date</th>\n'
    html += f'          <td>{book["acquisition"]["acquisition_date"]}</td>\n'
    html += '        </tr>\n'

    # Discontinued
    if discontinued:
        html += '        <tr>\n'
        html += '          <th class="vertical">Discontinued</th>\n'
        html += f'          <td>{discontinued}</td>\n'
        html += '        </tr>\n'

    # Audible Credits
    if book["acquisition"]["audible_credits"] is not None:
        html += '        <tr>\n'
        html += '          <th class="vertical">Audible Credits</th>\n'
        html += f'          <td>{book["acquisition"]["audible_credits"]}</td>\n'
        html += '        </tr>\n'

    # Price (Dollars)
    if price_in_dollars:
        html += '        <tr>\n'
        html += '          <th class="vertical">Price</th>\n'
        html += f'          <td>{price_in_dollars}</td>\n'
        html += '        </tr>\n'

    html += '      </tbody>\n'
    html += '    </table>\n'

    # Listener Notes
    html += '    <h2>Listener Notes</h2>\n'
    html += '    <table>\n'
    html += '      <thead>\n'
    html += '        <tr>\n'
    headers = ('Listener', 'Status', 'Finish Date', "Rating", "Comments")
    for header in headers:
        html += f'          <th>{header}</th>\n'
    html += '        </tr>\n'
    html += '      </thead>\n'
    html += '      <tbody>\n'
    for note in book["notes"]:
        html += '        <tr>\n'
        html += f'          <td>{note["username"]}</td>\n'
        html += f'          <td>{"" if note["status"] is None else note["status"]}</td>\n'
        html += f'          <td>{"" if note["finish_date"] is None else note["finish_date"]}</td>\n'
        rating = ""
        if note["rating_stars"] is not None:
            rating = str(note["rating_stars"]) + " " + note["rating_description"]
        html += f'          <td>{rating}</td>\n'
        html += f'          <td>{"" if note["comments"] is None else note["comments"]}</td>\n'
        html += '        </tr>\n'
    html += '    </table>\n'
    html += create_end_html()
    print(html)


def display_finished_books(conn):
    """
        title, authors, length, acquisition_date, finish_date, rating
    """
    print("Content-Type: text/html\r\n\r\n", end="")
    all_books_rs = select_all_books(conn)
    html = create_start_html()
    html += '    <h1>Audiobooks</h1>\n'
    html += create_finished_books_table_html(conn, all_books_rs)
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
