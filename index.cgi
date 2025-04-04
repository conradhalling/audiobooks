#!/Users/halto/src/conradhalling/audiobooks/venv310/bin/python3

"""
This script does not use the db package (yet).
"""

import cgi
import cgitb
cgitb.enable()
import os
import sqlite3
import sys
import textwrap

import dotenv
dotenv.load_dotenv()


########## Database interaction code


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


def select_author(conn, author_id):
    sql_select_author = """
        SELECT
            tbl_author.id,
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
    return result_set


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


def select_authors(conn):
    select_authors_sql = """
        SELECT
            tbl_author.id,
            tbl_author.surname,
            tbl_author.forename
        FROM
            tbl_author
        ORDER BY
            UPPER(tbl_author.surname),
            UPPER(tbl_author.forename)
    """
    cur = conn.execute(select_authors_sql)
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


def select_narrators_for_book(conn, book_id):
    sql_select_narrators_for_book = """
        SELECT
            tbl_narrator.id,
            tbl_narrator.surname,
            tbl_narrator.forename
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
            tbl_translator.surname,
            tbl_translator.forename
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


########## Data conversion functions


def get_audiobook_length(hours, minutes):
    """
    Return a string containing hours and minutes as "hh:mm".
    """
    length = f"{hours}:{minutes:02d}"
    return length


def get_author_name(surname, forename):
    """
    Convert the author's surname and forename into the author's full name.
    If surname is None (e.g., for Aeschylus or Homer), the author's full name
    is the forename.
    """
    if surname is None:
        name = forename
    else:
        name = surname + ", " + forename
    return name


def get_author_name_sort_key(surname, forename):
    """
    Convert the author's surname and forename into a case-independent sort key.
    """
    if surname is None:
        name = forename
    else:
        name = surname + " " + forename
    sort_key = name.upper()
    return sort_key


def get_rating(rating_stars, rating_description):
    """
    Return a rating string that is a combination of the rating_stars
    and rating_description values. Return an empty string if these
    are None.
    """
    rating = ""
    if rating_stars is not None:
        rating = str(rating_stars) + " " + rating_description
    return rating


def get_title_sort_key(title):
    """
    Return a case-insensitive sort key for the title by removing "The", "A",
    or "An" from the beginning of the title and converting the result to
    an uppercase string.
    """
    if title.startswith("A "):
        title_sort_key = title[2:]
    elif title.startswith("An "):
        title_sort_key = title[3:]
    elif title.startswith("The "):
        title_sort_key = title[4:]
    else:
        title_sort_key = title
    title_sort_key = title_sort_key.upper()
    return title_sort_key


########## HTML generation code


def create_about_html():
    html = """\
    <h1>About This Website</h1>
    <p>
      I have been recording the audiobooks I’ve listened to in an Excel
      spreadsheet since May, 2008. But a spreadsheet does a poor job of handling
      multiple authors for a book or multiple readings (listenings). So I wrote
      this tool to make it easier to keep track of the audiobooks I’ve listened
      to.
    </p>
    <p>
      Out of necessity, I wrote this application using Python CGI. This is
      because my shared hosting service supports PHP or Python CGI and not a
      newer protocol such as WSGI (e.g., Flask). Although CGI is dismissed these
      days as obsolete, CGI applications are fairly easy to write.
    </p>
    <p>
      Anyone is welcome to view the data, but at this time I am the only person
      who can log in to add new audiobooks or update existing audiobooks.
    </p>
    <p>
      The source code for this application is available at my
      <a href="https://github.com/conradhalling/audiobooks">GitHub
      repository</a>.
    </p>
    """
    return html


def create_all_authors_table_html(conn):
    # Get authors' forenames and surnames and combine them into a
    # case-dependent sort key and a full name.
    authors_result_set = select_authors(conn)
    name_list = []
    for row in authors_result_set:
        (author_id, surname, forename) = row
        author_name = get_author_name(surname, forename)
        author_name_sort_key = get_author_name_sort_key(surname, forename)
        name_list.append([author_id, author_name, author_name_sort_key])
    # Sort the list of lists.
    sorted_names_list = sorted(name_list, key=lambda attrs: attrs[2])

    html = ''
    html += '      <h1>Authors</h1>\n'
    html += '      <table id="authors">\n'
    html += '        <thead>\n'
    html += '          <tr>\n'
    html += '            <th>Author</th>\n'
    html += '            <th>Title</th>\n'
    html += '            <th>Rating</th>\n'
    html += '            <th class="nowrap">All Authors</th>\n'
    html += '            <th>Length</th>\n'
    html += '            <th>Acquired</th>\n'
    html += '            <th>Status</th>\n'
    html += '            <th>Finished</th>\n'
    html += '          </tr>\n'
    html += '        </thead>\n'
    html += '        <tbody>\n'
    for row in sorted_names_list:
        (author_id, author_name, sort_key) = row
        books_rs = select_books_for_author(conn, author_id)
        first_tr = True

        # Create a sorted list of book attributes.
        books_list = []
        for book_row in books_rs:
            (title, pub_date, audio_pub_date, hours, minutes, book_id) = book_row
            title_sort_key = get_title_sort_key(title)
            length = get_audiobook_length(hours, minutes)
            books_list.append((title, title_sort_key, pub_date, audio_pub_date, length, book_id))
        sorted_books_list = sorted(books_list, key=lambda tup: tup[1])

        for book in sorted_books_list:
            (title, title_sort_key, pub_date, audio_pub_date, length, book_id) = book

            # Select the acquisition date.
            acquisition_date = select_acquisition_date(conn, book_id)

            # Select the status, finished date (may be null), rating stars (may
            # be null), and rating description (is null if rating stars is null).
            # Create strings for the HTML output.
            rs = select_notes_for_book(conn, book_id)
            status = rs[0][1]
            finish_date = rs[0][2]
            if finish_date is None:
                finish_date = ""
            rating_stars = rs[0][3]
            rating_description = rs[0][4]
            rating = get_rating(rating_stars, rating_description)

            html += '          <tr>\n'
            if first_tr:
                html += f'            <td class="nowrap"><a href="index.cgi?author_id={author_id}">{author_name}</a></td>\n'
                first_tr = False
            else:
                html += '          <td></td>\n'
            html += f'            <td><a href="index.cgi?book_id={book_id}">{title}</a></td>\n'
            html += f'            <td class="nowrap">{rating}</td>\n'
            html += create_authors_td_html(conn, book_id)
            html += f'            <td class="right">{length}</td>\n'
            html += f'            <td class="nowrap">{acquisition_date}</td>\n'
            html += f'            <td>{status}</td>\n'
            html += f'            <td class="nowrap">{finish_date}</td>\n'
            html += '          </tr>\n'
    html += '        </tbody>\n'
    html += '      </table>\n'
    return html


def create_all_books_table_html(conn, books_result_set):
    """
    Create the HTML for all books.
    
    "⭥" is "\u2B65" or "&#x2B65;".
    """
    html =  '      <h1>Audiobooks</h1>\n'
    # html += '      <p class="filters" style="margin-bottom: 0;">\n'
    html += '      <div class="filters">\n'
    html += '        <strong>Filter by Status:</strong>\n'
    html += '        <input type="checkbox" id="new" title="Click this checkbox to toggle the visibility of new audiobooks." checked>\n'
    html += '        <label for="new" title="Click this checkbox to toggle the visibility of new audiobooks.">New</label>\n'
    html += '        <input type="checkbox" id="started" title="Click this checkbox to toggle the visibility of started audiobooks." checked>\n'
    html += '        <label for="started" title="Click this checkbox to toggle the visibility of started audiobooks.">Started</label>\n'
    html += '        <input type="checkbox" id="finished" title="Click this checkbox to toggle the visibility of finished audiobooks." checked>\n'
    html += '        <label for="finished" title="Click this checkbox to toggle the visibility of finished audiobooks.">Finished</label>\n'
    html += '      </div>\n'
    html += create_sortable_books_table_html(conn, books_result_set, filterable=True)
    return html


def create_authors_td_html(conn, book_id):
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
        author_name = get_author_name(author_surname, author_forename)
        if first_author:
            author_name_sort_key = get_author_name_sort_key(author_surname, author_forename)
            first_author = False
        author_string = f'<a href="?author_id={author_id}">{author_name}</a>'
        author_strings.append(author_string)
    html = f'            <td data-sortkey="{author_name_sort_key}" class="nowrap">{"<br>".join(author_strings)}</td>\n'
    return html

    
def create_book_html(book):
    """
    Book is dict from which all information about an audiobook can
    be extracted.
    """
    # Precompute cell values.
    length = "" if book["hours"] is None else f'{book["hours"]}:{book["minutes"]:02d}'
    book_pub_date = "" if book["book_pub_date"] is None else book["book_pub_date"]
    audio_pub_date = "" if book["audio_pub_date"] is None else book["audio_pub_date"]
    price_in_dollars = "" if book["acquisition"]["price_in_cents"] is None\
        else "$" + f'{float(book["acquisition"]["price_in_cents"] / 100):.2f}'
    discontinued = "" if book["acquisition"]["discontinued"] is None else "discontinued"
    
    author_strings = []
    author_html_strings = []
    for author_dict in book["authors"]:
        author_id = author_dict["author_id"]
        author_surname = author_dict["author_surname"]
        author_forename = author_dict["author_forename"]
        if author_surname is None:
            author_name = author_forename
        else:
            author_name = f"{author_forename} {author_surname}"
        author_html_string = f'<a href="?author_id={author_id}">{author_name}</a>'
        author_html_strings.append(author_html_string)
        author_strings.append(author_name)
    
    translator_html_strings = []
    for translator_dict in book["translators"]:
        translator_id = translator_dict["translator_id"]
        translator_forename = translator_dict["translator_forename"]
        translator_surname = translator_dict["translator_surname"]
        if translator_surname is None:
            translator_name = translator_forename
        else:
            translator_name = translator_forename + " " + translator_surname
        translator_string = f'<a href="?translator_id={translator_id}">{translator_name}</a>'
        translator_html_strings.append(translator_string)

    narrator_html_strings = []
    for narrator_dict in book["narrators"]:
        narrator_id = narrator_dict["narrator_id"]
        narrator_forename = narrator_dict["narrator_forename"]
        narrator_surname = narrator_dict["narrator_surname"]
        if narrator_surname is None:
            narrator_name = narrator_forename
        else:
            narrator_name = narrator_forename + " " + narrator_surname
        narrator_string = f'<a href="?narrator_id={narrator_id}">{narrator_name}</a>'
        narrator_html_strings.append(narrator_string)

    # Build the by authors string for the header.
    by_authors_string = author_strings[0]
    author_count = 1
    author_flag = True
    if len(author_strings) > 1:
        while author_flag:
            if author_count < len(author_strings) - 1:
                by_authors_string += ", " + author_strings[author_count]
                author_count += 1
            elif author_count == len(author_strings) - 1:
                by_authors_string += ", and " + author_strings[author_count]
                author_flag = False

    # Build and return HTML containing an h1 header, an h2 Book Information header
    # with an accompanying table, and an h2 Listener Notes header with an
    # accompanying table.
    html = ''
    html += f'      <h1><cite>{book["title"]}</cite><br>by {by_authors_string}</h1>\n'
    html += '      <h2>Book Information</h2>\n'
    html += '      <table>\n'
    html += '        <tbody class="vertical">\n'

    # Title
    html += '          <tr>\n'
    html += '            <th class="vertical">Title</th>\n'
    html += f'            <td><cite>{book["title"]}</cite></td>\n'
    html += '          </tr>\n'

    # Authors
    html += '          <tr>\n'
    html += '            <th class="vertical">Author{}</th>\n'.format(
        "s" if len(author_strings) > 1 else "")
    html += f'            <td>{"<br>".join(author_html_strings)}</td>\n'
    html += '          </tr>\n'

    # Length
    html += '          <tr>\n'
    html += '            <th class="vertical nowrap">Length (hr:min)</th>\n'
    html += f'            <td>{length}</td>\n'
    html += '          </tr>\n'

    # Translators
    if len(translator_html_strings) > 0:
        html += '          <tr>\n'
        html += '            <th class="vertical">Translator{}</th>\n'.format(
            "s" if len(translator_html_strings) > 1 else "")
        html += f'            <td>{", ".join(translator_html_strings)}</td>\n'
        html += '          </tr>\n'

    # Narrators
    html += '          <tr>\n'
    html += '            <th class="vertical">Narrator{}</th>\n'.format(
        "s" if len(narrator_html_strings) != 1 else "")
    html += f'            <td>{", ".join(narrator_html_strings)}</td>\n'
    html += '          </tr>\n'

    # Book Pub. Date
    if book_pub_date:
        html += '          <tr>\n'
        html += '            <th class="vertical nowrap">Book Pub. Date</th>\n'
        html += f'            <td>{book_pub_date}</td>\n'
        html += '          </tr>\n'

    # Audio Pub. Date
    if audio_pub_date:
        html += '          <tr>\n'
        html += '            <th class="vertical nowrap">Audio Pub. Date</th>\n'
        html += f'            <td>{audio_pub_date}</td>\n'
        html += '          </tr>\n'

    # Acquired By
    html += '          <tr>\n'
    html += '            <th class="vertical nowrap">Acquired By</th>\n'
    html += f'            <td>{book["acquisition"]["username"]}</td>\n'
    html += '          </tr>\n'

    # Vendor
    html += '          <tr>\n'
    html += '            <th class="vertical">Vendor</th>\n'
    html += f'            <td>{book["acquisition"]["vendor_name"]}</td>\n'
    html += '          </tr>\n'

    # Acquisition Type
    html += '          <tr>\n'
    html += '            <th class="vertical nowrap">Acquisition Type</th>\n'
    html += f'            <td>{book["acquisition"]["acquisition_type"]}</td>\n'
    html += '          </tr>\n'

    # Acquisition Date
    html += '          <tr>\n'
    html += '            <th class="vertical nowrap">Acquisition Date</th>\n'
    html += f'            <td>{book["acquisition"]["acquisition_date"]}</td>\n'
    html += '          </tr>\n'

    # Discontinued
    if discontinued:
        html += '          <tr>\n'
        html += '            <th class="vertical">Discontinued</th>\n'
        html += f'            <td>{discontinued}</td>\n'
        html += '          </tr>\n'

    # Audible Credits
    if book["acquisition"]["audible_credits"] is not None:
        html += '          <tr>\n'
        html += '            <th class="vertical nowrap">Audible Credits</th>\n'
        html += f'            <td>{book["acquisition"]["audible_credits"]}</td>\n'
        html += '          </tr>\n'

    # Price (Dollars)
    if price_in_dollars:
        html += '          <tr>\n'
        html += '            <th class="vertical">Price</th>\n'
        html += f'            <td>{price_in_dollars}</td>\n'
        html += '          </tr>\n'

    html += '        </tbody>\n'
    html += '      </table>\n'

    # Listener Notes
    html += '      <h2>Listener Notes</h2>\n'
    html += '      <table>\n'
    html += '        <thead>\n'
    html += '          <tr>\n'
    headers = ('Listener', 'Status', 'Finished', "Rating", "Comments")
    for header in headers:
        html += f'            <th>{header}</th>\n'
    html += '          </tr>\n'
    html += '        </thead>\n'
    html += '        <tbody>\n'
    for note in book["notes"]:
        html += '          <tr>\n'
        html += f'            <td>{note["username"]}</td>\n'
        html += f'            <td>{"" if note["status"] is None else note["status"]}</td>\n'
        html += f'            <td class="nowrap">{"" if note["finish_date"] is None else note["finish_date"]}</td>\n'
        rating = ""
        if note["rating_stars"] is not None:
            rating = str(note["rating_stars"]) + " " + note["rating_description"]
        html += f'            <td class="nowrap">{rating}</td>\n'
        html += f'            <td>{"" if note["comments"] is None else note["comments"]}</td>\n'
        html += '          </tr>\n'
    html += '      </table>\n'
    return html


def create_end_html():
    end_html = """\
            </main>
          </body>
        </html>"""
    return textwrap.dedent(end_html)


def create_sortable_books_table_html(conn, books_result_set, filterable=False):
    """
    The all books table is filterable.
    The books table associated with an author is not filterable or hideable.
    """
    th_tool_tip = "Click this header to sort the table by the values in this column."
    html = ''
    if filterable:
        html += '      <table id="audiobooks" class="filterable">\n'
    else:
        html += '      <table id="audiobooks">\n'
    html += '        <thead>\n'
    html += '          <tr>\n'

    # Since the table is sorted by title, put the up arrow symbol in the
    # span element.
    html += f'            <th class="sortable nowrap" title="{th_tool_tip}">Title <span>⭡</span></th>\n'
    html += f'            <th class="sortable nowrap" title="{th_tool_tip}">Authors <span>⭥</span></th>\n'
    html += f'            <th class="sortable nowrap" title="{th_tool_tip}">Rating <span>⭥</span></th>\n'
    html += f'            <th class="sortable nowrap" title="{th_tool_tip}">Length <span>⭥</span></th>\n'
    html += f'            <th class="sortable nowrap" title="{th_tool_tip}">Acquired <span>⭥</span></th>\n'
    html += f'            <th class="sortable nowrap" title="{th_tool_tip}">Status <span>⭥</span></th>\n'
    html += f'            <th class="sortable nowrap" title="{th_tool_tip}">Finished <span>⭥</span></th>\n'
    html += '          </tr>\n'
    html += '        </thead>\n'
    html += '        <tbody>\n'

    # Add a title sort key to the row and sort by the title sort key.
    books_list = []
    for row in books_result_set:
        book_attrs = list(row)
        title = book_attrs[0]
        title_sort_key = get_title_sort_key(title)
        book_attrs.append(title_sort_key)
        books_list.append(book_attrs)
    sorted_book_attrs = sorted(books_list, key=lambda attrs: attrs[6])

    # Get the book attributes for the table.
    for book_attrs in sorted_book_attrs:
        [title, book_pub_date, audio_pub_date, hours, minutes, book_id, title_sort_key] = book_attrs
        # Create a key for sorting by length.
        length_sort_key = 60 * int(hours) + int(minutes)
        # Convert hours and minutes to an hh:mm string.
        length = get_audiobook_length(hours, minutes)
        # Select the acquisition date.
        acquisition_date = select_acquisition_date(conn, book_id)
        # Select the status, finished date (may be null), rating stars (may
        # be null), and rating description (is null if rating stars is null).
        # Create strings for the HTML output.
        rs = select_notes_for_book(conn, book_id)
        status = rs[0][1]
        finish_date = rs[0][2]
        if finish_date is None:
            finish_date = ""
        rating_stars = rs[0][3]
        rating_description = rs[0][4]
        rating = get_rating(rating_stars, rating_description)

        # Create table rows for all books, reporting only the first finished date.
        html += f'          <tr class="{status.lower()}">\n'
        html += f'            <td data-sortkey="{title_sort_key}"><a href="?book_id={book_id}">{title}</a></td>\n'
        html += create_authors_td_html(conn, book_id)
        html += f'            <td class="nowrap">{rating}</td>\n'
        html += f'            <td data-sortkey="{length_sort_key}" class="right">{length}</td>\n'
        html += f'            <td>{acquisition_date}</td>\n'
        html += f'            <td>{status}</td>\n'
        html += f'            <td>{finish_date}</td>\n'
        html += '          </tr>\n'

    html += '        </tbody>\n'
    html += '      </table>\n'
    return html


def create_start_html(body_class="tables"):
    """
    body_class is "tables" when data tables are shown, in which case the
    body's margins are reduced to the minimum in a narrow viewport.

    body_class is "about" when the about page is displayed; there is
    sufficient room on the page that the margins can remain the same.
    """
    start_html = fr"""        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Audiobooks</title>
            <link rel="stylesheet" href="styles.css">
            <script src="js/main.js" type="module"></script>
          </head>
          <body class="{body_class}">
            <header>
              <nav>
                <ul>
                  <li class="logo" style="min-width: 13rem;"><a href="index.cgi">🎧<em>Audio</em>books📚</a></li>
                  <li><a href="index.cgi">Audiobooks</a></li>
                  <li><a href="index.cgi?authors=all">Authors</a></li>
                  <li><a href="index.cgi?about=about">About</a></li>
                  <li class="blog"><a href="https://conradhalling.com/blog/">Blog</a></li>
                  <!--
                  <li><a href="new.cgi">New</a></li>
                  <li><a href="login.cgi">Log In</a></li>
                  -->
                </ul>
              </nav>
            </header>
            <main class="{body_class}">
        """
    return textwrap.dedent(start_html)


########## Get data code.


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
        (translator_id, translator_surname, translator_forename) = row
        translator_dict = {
            "translator_id": translator_id,
            "translator_surname": translator_surname,
            "translator_forename": translator_forename,
        }
        translators_list.append(translator_dict)
    book_dict["translators"] = translators_list

    narrators_rs = select_narrators_for_book(conn, book_id)
    narrators_list = []
    for row in narrators_rs:
        (narrator_id, narrator_surname, narrator_forename) = row
        narrator_dict = {
            "narrator_id": narrator_id,
            "narrator_surname": narrator_surname,
            "narrator_forename": narrator_forename,
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


########## Display code.


def display_about():
    html = create_start_html(body_class="about")
    html += create_about_html()
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_all_authors(conn):
    html = create_start_html(body_class="tables")
    html += create_all_authors_table_html(conn)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_all_books(conn):
    """
    title, authors, length, acquisition_date, status, finish_date, rating.
    """
    all_books_rs = select_all_books(conn)
    html = create_start_html(body_class="tables")
    html += create_all_books_table_html(conn, all_books_rs)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_author(conn, author_id):
    html = create_start_html(body_class="tables")
    author_id, author_surname, author_forename = select_author(conn, author_id)
    if author_surname is None:
        author_name = author_forename
    else:
        author_name = author_forename + " " + author_surname
    html += f'    <h1>Audiobooks by {author_name}</h1>\n'
    books_for_author_rs = select_books_for_author(conn, author_id)
    html += create_sortable_books_table_html(conn, books_for_author_rs)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_book(conn, book_id):
    html = create_start_html(body_class="tables")
    book = get_book_data(conn, book_id)
    html += create_book_html(book)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def main():
    """
    Carefully manage exceptions to make sure the database file is closed.
    
    Carefully manage HTTP Content-Type headers. Each display function prints
    its own Content-Type header so the application can return HTML, an image,
    CSV, JSON, etc.
    """
    try:
        conn = None
        conn = connect()
        fs = cgi.FieldStorage()
        if "author_id" in fs:
            display_author(conn, fs["author_id"].value)
        elif "book_id" in fs:
            display_book(conn, fs["book_id"].value)
        elif "authors" in fs:
            display_all_authors(conn)
        elif "about" in fs:
            display_about()
        else:
            display_all_books(conn)
    except Exception:
        # Send a Content-Type header before printing the exception.
        print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
        print(cgitb.html(sys.exc_info()))
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
