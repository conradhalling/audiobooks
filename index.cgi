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

########## Configuration code.

def get_index_path():
    """
    Return the webserver's path to the index.cgi script, using the
    AUDIOBOOKS_WEBDIR environment variable.
    """
    index_path = f"{os.environ.get('AUDIOBOOKS_WEBDIR')}index.cgi"
    return index_path


def get_js_dir_path():
    """
    Return the webserver's path to the js directory, using the
    AUDIOBOOKS_WEBDIR environment variable.
    """
    js_dir_path = f"{os.environ.get('AUDIOBOOKS_WEBDIR')}js/"
    return js_dir_path


def get_styles_path():
    """
    Return the webserver's path to the styles.css file, using the
    AUDIOBOOKS_WEBDIR environment variable.
    """
    styles_path = f"{os.environ.get('AUDIOBOOKS_WEBDIR')}styles.css"
    return styles_path


########## Database interaction code

def connect():
    db_file = os.environ.get("SQLITE3_DB")
    conn = sqlite3.connect(database=db_file)
    sql_pragma_foreign_keys = "PRAGMA foreign_keys = ON"
    conn.execute(sql_pragma_foreign_keys)
    return conn


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


def select_all_author_ids(conn):
    select_author_ids_sql = """
        SELECT
            tbl_author.id
        FROM
            tbl_author
    """
    cur = conn.execute(select_author_ids_sql)
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_all_book_ids(conn):
    sql_select_all_book_ids = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
    """
    cur = conn.execute(sql_select_all_book_ids)
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


def select_author_ids_for_book(conn, book_id):
    sql_select_author_ids_for_book = """
        SELECT
            tbl_author.id
        FROM
            tbl_book_author
            INNER JOIN tbl_author
                ON tbl_book_author.author_id = tbl_author.id
        WHERE
            tbl_book_author.book_id = ?
    """
    cur = conn.execute(sql_select_author_ids_for_book, (book_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_book(conn, book_id):
    """
    Given a book's ID, select the book's attributes.
    """
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
    result_set = cur.fetchone()
    cur.close()
    return result_set


def select_book_ids_for_author(conn, author_id):
    sql_select_book_ids_for_author = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
            INNER JOIN tbl_book_author
                ON tbl_book.id = tbl_book_author.book_id
        WHERE
            tbl_book_author.author_id = ?
    """
    cur = conn.execute(sql_select_book_ids_for_author, (author_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_books_for_author(conn, author_id):
    """
    Deprecated.
    """
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


def select_book_ids_for_narrator(conn, narrator_id):
    sql_select_book_ids_for_narrator = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
            INNER JOIN tbl_book_narrator
                ON tbl_book.id = tbl_book_narrator.book_id
        WHERE
            tbl_book_narrator.narrator_id = ?
    """
    cur = conn.execute(sql_select_book_ids_for_narrator, (narrator_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_book_ids_for_translator(conn, translator_id):
    sql_select_book_ids_for_translator = """
        SELECT
            tbl_book.id
        FROM
            tbl_book
            INNER JOIN tbl_book_translator
                ON tbl_book.id = tbl_book_translator.book_id
        WHERE
            tbl_book_translator.translator_id = ?
    """
    cur = conn.execute(sql_select_book_ids_for_translator, (translator_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_narrator(conn, narrator_id):
    sql_select_narrator = """
        SELECT
            tbl_narrator.id,
            tbl_narrator.surname,
            tbl_narrator.forename
        FROM
            tbl_narrator
        WHERE
            tbl_narrator.id = ?
    """
    cur = conn.execute(sql_select_narrator, (narrator_id,))
    result_set = cur.fetchone()
    cur.close()
    return result_set


def select_narrator_ids_for_book(conn, book_id):
    sql_select_narrator_ids_for_book = """
        SELECT
            tbl_narrator.id
        FROM
            tbl_book_narrator
            INNER JOIN tbl_narrator
                ON tbl_book_narrator.narrator_id = tbl_narrator.id
        WHERE
            tbl_book_narrator.book_id = ?
    """
    cur = conn.execute(sql_select_narrator_ids_for_book, (book_id,))
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
    """
    Select notes in chronological order using tbl_note.id.
    """
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
            tbl_note.id
    """
    cur = conn.execute(sql_select_notes_for_book, (book_id,))
    result_set = cur.fetchall()
    cur.close()
    return result_set


def select_total_acquired(conn):
    sql_select_total_acquired = """
        SELECT
            COUNT(tbl_acquisition.acquisition_date)
        FROM
            tbl_acquisition
    """
    cur = conn.execute(sql_select_total_acquired)
    result_set = cur.fetchone()
    cur.close()
    return result_set[0]


def select_total_distinct_finished(conn):
    sql_select_total_distinct_finished = """
        SELECT
            COUNT(DISTINCT tbl_book.id) as books_finished
        FROM
            tbl_book
            INNER JOIN tbl_note
                ON tbl_book.id = tbl_note.book_id
        WHERE
            tbl_note.finish_date IS NOT NULL
    """
    cur = conn.execute(sql_select_total_distinct_finished)
    result_set = cur.fetchone()
    cur.close()
    return result_set[0]


def select_total_finished(conn):
    sql_select_total_finished = """
        SELECT
            COUNT(tbl_note.finish_date)
        FROM
            tbl_note
        WHERE
            tbl_note.finish_date IS NOT NULL
    """
    cur = conn.execute(sql_select_total_finished)
    result_set = cur.fetchone()
    cur.close()
    return result_set[0]


def select_total_unfinished(conn):
    sql_select_total_unfinished = """
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
    cur = conn.execute(sql_select_total_unfinished)
    result_set = cur.fetchone()
    cur.close()
    return result_set[0]


def select_translator(conn, translator_id):
    sql_select_translator = """
        SELECT
            tbl_translator.id,
            tbl_translator.surname,
            tbl_translator.forename
        FROM
            tbl_translator
        WHERE
            tbl_translator.id = ?
    """
    cur = conn.execute(sql_select_translator, (translator_id,))
    result_set = cur.fetchone()
    cur.close()
    return result_set


def select_translator_ids_for_book(conn, book_id):
    sql_select_translator_ids_for_book = """
        SELECT
            tbl_translator.id
        FROM
            tbl_book_translator
            INNER JOIN tbl_translator
                ON tbl_book_translator.translator_id = tbl_translator.id
        WHERE
            tbl_book_translator.book_id = ?
    """
    cur = conn.execute(sql_select_translator_ids_for_book, (book_id,))
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


def select_year_counts(conn):
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
    cur = conn.execute(sql_select_year_counts)
    result_set = cur.fetchall()
    cur.close()
    return result_set


########## Data conversion functions


def get_rating(note):
    """
    Return a rating string that is a combination of the rating_stars
    and rating_description values. Return an empty string if these
    are None.
    """
    rating = ""
    if note["rating_stars"] is not None:
        rating = str(note["rating_stars"]) + " " + note["rating_description"]
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


def create_404_html():
    html = """\
    <h1>404: Page Not Found</h1>
    <p>
      Sorry, we've misplaced that URL or it's pointing to something that doesn't
      exist.
    </p>
    """
    return html


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


def create_all_authors_table_html(authors):
    """
    authors is a list of author data records sorted by the authors' last names
    using the name_sort_key attribute as the sort key.

    The author attribues are:
        id
        surname
        forename
        display_name
        reverse_name
        name_sort_key
        books -- a list of book dicts
    """
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

    index_path = get_index_path()
    for author in authors:
        sorted_books = sorted(author["books"], key=lambda book: book["title_sort_key"])
        first_tr = True
        for book in sorted_books:
            html += '          <tr>\n'
            if first_tr:
                html += f"""            <td class="nowrap"><a href="{index_path}?author_id={author["id"]}">{author["reverse_name"]}</a></td>\n"""
                first_tr = False
            else:
                html += '          <td></td>\n'
            html += f"""            <td><a href="{index_path}?book_id={book["id"]}">{book["title"]}</a></td>\n"""
            html += f'            <td class="nowrap">{book["rating"]}</td>\n'
            html += create_authors_td_html(book["authors"])
            html += f'            <td class="right">{book["length"]}</td>\n'
            html += f'            <td class="nowrap">{book["acquisition_date"]}</td>\n'
            html += f'            <td>{book["status_string"]}</td>\n'
            html += f'            <td class="nowrap">{book["finish_date_string"]}</td>\n'
            html += '          </tr>\n'
    html += '        </tbody>\n'
    html += '      </table>\n'
    return html


def create_summaries_html(summaries):
    html = '      <h1>Summaries</h1>\n'
    html += '      <h2>Annual Totals</h2>\n'
    html += '      <table>\n'
    html += '        <caption>Number of audiobooks acquired and finished each year</caption>\n'
    html += '        <thead>\n'
    html += '          <tr>\n'
    html += '            <th>Year</th>\n'
    html += '            <th>Acquired</th>\n'
    html += '            <th>Finished</th>\n'
    html += '          </tr>\n'
    html += '        </thead>\n'
    html += '        <tbody>\n'
    for row in summaries["year_counts"]:
        html += '        <tr>\n'
        html += f'          <td class="right">{row["year"]}</td>\n'
        html += f'          <td class="right">{row["acquired"]}</td>\n'
        html += f'          <td class="right">{row["finished"]}</td>\n'
        html += f'        </tr>\n'
    html += '        </tbody>\n'
    html += '      </table>\n'

    html += '      <h2>Grand Totals</h2>\n'
    html += '      <table>\n'
    html += '        <caption>All Audiobooks Finished includes multiple listens of audiobooks</caption>'
    html += '        <tbody>\n'
    html += '          <tr>\n'
    html += '            <th>Audiobooks Acquired</th>\n'
    html += f'            <td class="right">{summaries["totals"]["acquired"]}</td>\n'
    html += '          </tr>\n'
    html += '          <tr>\n'
    html += '            <th>Distinct Audiobooks Finished</th>\n'
    html += f'            <td class="right">{summaries["totals"]["distinct_finished"]}</td>\n'
    html += '          </tr>\n'
    html += '          <tr>\n'
    html += '            <th>Audiobooks Not Finished</th>\n'
    html += f'            <td class="right">{summaries["totals"]["not_finished"]}</td>\n'
    html += '          </tr>\n'
    html += '          <tr>\n'
    html += '            <th>All Audiobooks Finished</th>\n'
    html += f'            <td class="right">{summaries["totals"]["all_finished"]}</td>\n'
    html += '          </tr>\n'
    html += '        </tbody>\n'
    html += '      </table>\n'
    return html


def create_all_books_table_html(books):
    """
    Create the HTML for all books.
    """
    html =  '      <h1>Audiobooks</h1>\n'
    html += '      <div class="filters">\n'
    html += '        <strong>Filter by Status:</strong>\n'
    html += '        <input type="checkbox" id="new" title="Click this checkbox to toggle the visibility of new audiobooks." checked>\n'
    html += '        <label for="new" title="Click this checkbox to toggle the visibility of new audiobooks.">New</label>\n'
    html += '        <input type="checkbox" id="started" title="Click this checkbox to toggle the visibility of started audiobooks." checked>\n'
    html += '        <label for="started" title="Click this checkbox to toggle the visibility of started audiobooks.">Started</label>\n'
    html += '        <input type="checkbox" id="finished" title="Click this checkbox to toggle the visibility of finished audiobooks." checked>\n'
    html += '        <label for="finished" title="Click this checkbox to toggle the visibility of finished audiobooks.">Finished</label>\n'
    html += '      </div>\n'
    html += create_sortable_books_table_html(books, filterable=True)
    return html


def create_author_html(author):
    """
    author is a dict containing information about the author and the books the
    author has created.
    """
    html = ""
    html += f'    <h1>Audiobooks Created by {author["display_name"]}</h1>\n'
    html += create_sortable_books_table_html(author["books"])
    return html


def create_authors_td_html(authors):
    """
    authors is a list of dicts containing author data.
    """
    index_path = get_index_path()
    author_strings = []
    first_author = True
    for author in authors:
        if first_author:
            # The sort key comes from the name of the first author.
            author_name_sort_key = author["name_sort_key"]
            first_author = False
        author_string = f'<a href="{index_path}?author_id={author["id"]}">{author["reverse_name"]}</a>'
        author_strings.append(author_string)
    html = f'            <td data-sortkey="{author_name_sort_key}" class="nowrap">{"<br>".join(author_strings)}</td>\n'
    return html


def create_book_html(book):
    """
    book is a dict from which all information about an audiobook can
    be extracted.
    """
    index_path = get_index_path()

    # Precompute cell values.
    # length = "" if book["hours"] is None else f'{book["hours"]}:{book["minutes"]:02d}'
    book_pub_date = "" if book["book_pub_date"] is None else book["book_pub_date"]
    audio_pub_date = "" if book["audio_pub_date"] is None else book["audio_pub_date"]
    price_in_dollars = "" if book["acquisition"]["price_in_cents"] is None\
        else "$" + f'{float(book["acquisition"]["price_in_cents"] / 100):.2f}'
    discontinued = "" if book["acquisition"]["discontinued"] is None else "discontinued"
    
    author_strings = []
    author_html_strings = []
    for author in book["authors"]:
        author_name = author['display_name']
        author_html_string = f"""<a href="{index_path}?author_id={author['id']}">{author['reverse_name']}</a>"""
        author_html_strings.append(author_html_string)
        author_strings.append(author_name)
    
    translator_html_strings = []
    for translator in book["translators"]:
        translator_name = translator['display_name']
        translator_string = f"""<a href="{index_path}?translator_id={translator['id']}">{translator_name}</a>"""
        translator_html_strings.append(translator_string)

    narrator_html_strings = []
    for narrator in book["narrators"]:
        narrator_name = narrator['display_name']
        narrator_string = f"""<a href="{index_path}?narrator_id={narrator['id']}">{narrator_name}</a>"""
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
                if len(author_strings) == 2:
                    join_string = " and "
                else:
                    join_string = ", and "
                by_authors_string += join_string + author_strings[author_count]
                author_flag = False

    # Build and return HTML containing an h1 header, an h2 Audiobook Information header
    # with an accompanying table, and an h2 Listener Notes header with an
    # accompanying table.
    html = ''
    html += f'      <h1><cite>{book["title"]}</cite><br>by {by_authors_string}</h1>\n'
    html += '      <h2>Audiobook Information</h2>\n'
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
    html += f'            <td>{book["length"]}</td>\n'
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


def create_narrator_html(narrator):
    """
    narrator is a dict containing information about the narrator and the books the
    narrator has narrated.
    """
    html = ""
    html += f'    <h1>Audiobooks Narrated by {narrator["display_name"]}</h1>\n'
    html += create_sortable_books_table_html(narrator["books"])
    return html


def create_sortable_books_table_html(books, filterable=False):
    """
    The all books table is filterable; the books table associated with an
    author, translator, or narrator is not filterable.
    """
    index_path = get_index_path()

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

    # Sort by the title sort key.
    sorted_books = sorted(books, key=lambda book: book["title_sort_key"])

    # Get the book attributes for the table.
    for book in sorted_books:
        # Create table rows for all books, reporting only the first finished date.
        html += f"""          <tr class="{book['notes'][0]['status'].lower()}">\n"""
        html += f"""            <td data-sortkey="{book['title_sort_key']}"><a href="{index_path}?book_id={book['id']}">{book['title']}</a></td>\n"""
        html += create_authors_td_html(book["authors"])
        html += f"""            <td class="nowrap">{book['rating']}</td>\n"""
        html += f"""            <td data-sortkey="{book['length_sort_key']}" class="right">{book["length"]}</td>\n"""
        html += f"""            <td>{book["acquisition"]["acquisition_date"]}</td>\n"""
        html += f"""            <td>{book["notes"][0]["status"]}</td>\n"""
        html += f'            <td>{book["finish_date_string"]}</td>\n'
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

    This function requires the AUDIOBOOKS_WEBDIR environment variable
    for determing the locations of styles.css and js/main.js.
    """
    index_path = get_index_path()
    js_dir_path = get_js_dir_path()
    styles_path = get_styles_path()
    start_html = fr"""        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Audiobooks</title>
            <link rel="stylesheet" href="{styles_path}">
            <script src="{js_dir_path}main.js" type="module"></script>
          </head>
          <body class="{body_class}">
            <header class="header">
              <a href="{index_path}" class="logo">🎧<em>Audio</em>books📚</a>
              <input class="side-menu" type="checkbox" id="side-menu">
              <label class="hamb" for="side-menu">
                <span class="hamb-line"></span>
              </label>
              <nav class="nav">
                <ul class="menu">
                  <li><a href="{index_path}">Audiobooks</a></li>
                  <li><a href="{index_path}?authors">Authors</a></li>
                  <li><a href="{index_path}?summaries">Summaries</a></li>
                  <li><a href="{index_path}?about">About</a></li>
                  <li class="blog"><a href="https://conradhalling.com/blog/">Blog</a></li>
                  <!--
                  <li><a href="new.cgi">New</a></li>
                  <li><a href="{index_path}?login">Log In</a></li>
                  -->
                </ul>
              </nav>
            </header>
            <main class="{body_class}">
        """
    return textwrap.dedent(start_html)


def create_translator_html(translator):
    """
    translator is a dict containing information about the translator and the books the
    translator has translated.
    """
    html = ""
    html += f'    <h1>Audiobooks Translated by {translator["display_name"]}</h1>\n'
    html += create_sortable_books_table_html(translator["books"])
    return html


########## Get data code.


def get_all_authors_data(conn):
    """
    Return a list of author records, where the list is sorted by the
    author["name_sort_key"] attribute.
    """
    authors = []
    author_ids_rs = select_all_author_ids(conn)
    for author_id_rs in author_ids_rs:
        (author_id,) = author_id_rs
        author = get_author_data_with_books(conn, author_id)
        authors.append(author)
    sorted_authors = sorted(authors, key=lambda author: author["name_sort_key"])
    return sorted_authors


def get_all_books_data(conn):
    """
    Return a list of book records, where the list is sorted by the
    book["title_sort_key"] attribute.
    """
    books = []
    book_ids_rs = select_all_book_ids(conn)
    for book_id_rs in book_ids_rs:
        (book_id,) = book_id_rs
        book = get_book_data(conn, book_id)
        books.append(book)
    sorted_books = sorted(books, key=lambda book: book["title_sort_key"])
    return sorted_books


def get_author_data(conn, author_id):
    """
    Return None if the author doesn't exist.
    Otherwise, return a dict containing the author's data.

    The author attribues are:
        id
        surname
        forename
        display_name  -- forename + " " + surname
        reverse_name  -- surname + ", " + forename
        name_sort_key -- (surname + " " + forename).upper()
    """
    author = None
    author_rs = select_author(conn, author_id)
    if author_rs is not None:
        # Store the attributes selected from the database.
        id, surname, forename = author_rs
        author = {
            "id": id,
            "surname": surname,
            "forename": forename
        }

        # Compute the display_name attribute.
        if author["surname"] is None:
            author["display_name"] = author["forename"]
        else:
            author["display_name"] = author["forename"] + " " + author["surname"]

        # Compute the reverse_name attribute.
        if surname is None:
            author["reverse_name"] = author["forename"]
        else:
            author["reverse_name"] = author["surname"] + ", " + author["forename"]

        # Compute the name_sort_key attribute.
        if surname is None:
            name_sort_key = author["forename"].upper()
        else:
            name_sort_key = author["surname"] + " " + author["forename"]
        author["name_sort_key"] = name_sort_key.upper() 
    return author


def get_author_data_with_books(conn, author_id):
    """
    Return None if the author doesn't exist.
    Otherwise, return a dict containing the author's data.

    The author attribues are:
        id
        surname
        forename
        display_name
        reverse_name
        name_sort_key
        books -- a list of book dicts
    """
    author = get_author_data(conn, author_id)
    if author is not None:
        # Get the books written by the author and store the list as the
        # books attribute.
        author["books"] = []
        book_ids_rs = select_book_ids_for_author(conn, author_id)
        for book_id_rs in book_ids_rs:
            (book_id,) = book_id_rs
            book = get_book_data(conn, book_id)
            author["books"].append(book)
    return author


def get_authors_for_book(conn, book_id):
    author_ids_rs = select_author_ids_for_book(conn, book_id)
    authors = []
    for author_id_rs in author_ids_rs:
        (author_id,) = author_id_rs
        author = get_author_data(conn, author_id)
        authors.append(author)
    return authors


def get_book_data(conn, book_id):
    """
    Return None if the book_id is not in the database.
    Otherwise, return a dict containing the book's information.
    """
    book_rs = select_book(conn, book_id)
    if book_rs is None:
        return None

    (id, title, book_pub_date, audio_pub_date, hours, minutes,) = book_rs
    book = {
        "id": id,
        "title": title,
        "book_pub_date": book_pub_date,
        "audio_pub_date": audio_pub_date,
        "hours": hours,
        "minutes": minutes,
    }
    book["authors"] = get_authors_for_book(conn, book_id)
    book["translators"] = get_translators_for_book(conn, book_id)
    book["narrators"] = get_narrators_for_book(conn, book_id)

    # Acquisition
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
    book["acquisition"] = acquisition_dict

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
    book["notes"] = notes_list

    # Create computed attributes.
    # Create a key for sorting by title.
    book["title_sort_key"] = get_title_sort_key(book["title"])
    # Create a key for sorting by length.
    book["length_sort_key"] = 60 * int(book["hours"]) + int(book["minutes"])
    # Convert hours and minutes to an hh:mm string.
    book["length"] = f'{book["hours"]}:{book["minutes"]:02d}'
    # Get a combined rating for the book from the first notes record.
    book["rating"] = get_rating(book["notes"][0])
    # Convert the finish_date to a string.
    book["finish_date_string"] = book["notes"][0]["finish_date"]
    if book["finish_date_string"] is None:
        book["finish_date_string"] = ""
    # Convert the status to a string.
    book["status_string"] = book["notes"][0]["status"]
    if book["status_string"] is None:
        book["status_string"] = ""
    # Compute the acquisition_date attribute.
    book["acquisition_date"] = book["acquisition"]["acquisition_date"]
    return book


def get_narrator_data(conn, narrator_id):
    """
    Return None if the narrator doesn't exist.
    Otherwise, return a dict containing the narrator's data.

    The narrator attributes are:
        id
        surname
        forename
        display_name
    """
    narrator = None
    narrator_rs = select_narrator(conn, narrator_id)
    if narrator_rs is not None:
        # Store the attributes selected from the database.
        id, surname, forename = narrator_rs
        narrator = {
            "id": id,
            "surname": surname,
            "forename": forename
        }

        # Compute the display_name attribute.
        if narrator["surname"] is None:
            narrator["display_name"] = narrator["forename"]
        else:
            narrator["display_name"] = narrator["forename"] + " " + narrator["surname"]
    return narrator


def get_narrator_data_with_books(conn, narrator_id):
    """
    Return None if the narrator doesn't exist.
    Otherwise, return a dict containing the narrator's data.

    The narrator attributes are:
        id
        surname
        forename
        display_name
        books -- a list of book dicts
    """
    narrator = get_narrator_data(conn, narrator_id)
    if narrator is not None:
        # Get the books narrated by the narrator and store the list as the
        # books attribute.
        narrator["books"] = []
        book_ids_rs = select_book_ids_for_narrator(conn, narrator_id)
        for book_id_rs in book_ids_rs:
            (book_id,) = book_id_rs
            book = get_book_data(conn, book_id)
            narrator["books"].append(book)
    return narrator


def get_narrators_for_book(conn, book_id):
    narrator_ids_rs = select_narrator_ids_for_book(conn, book_id)
    narrators = []
    for narrator_id_rs in narrator_ids_rs:
        (narrator_id,) = narrator_id_rs
        narrator = get_narrator_data(conn, narrator_id)
        narrators.append(narrator)
    return narrators


def get_summaries_data(conn):
    summaries = {}

    # year_counts is a list of dicts with keys "year", "acquired", and
    # finished" and values the year, the number of books acquired that
    # year, and the number of books finished that year.
    year_counts_rs = select_year_counts(conn)
    year_counts = []
    for row in year_counts_rs:
        (year, acquired, finished) = row
        year_dict = {
            "year": year,
            "acquired": acquired,
            "finished": finished,
        }
        year_counts.append(year_dict)
    summaries["year_counts"] = year_counts

    # totals is a dict containing acquired, distinct_finished, not_finished,
    # and all_finished totals.
    totals = {
        "acquired": select_total_acquired(conn),
        "distinct_finished": select_total_distinct_finished(conn),
        "not_finished": select_total_unfinished(conn),
        "all_finished": select_total_finished(conn),
    }
    summaries["totals"] = totals
    return summaries


def get_translator_data(conn, translator_id):
    """
    Return None if the translator doesn't exist.
    Otherwise, return a dict containing the translator's data.

    The translator attributes are:
        id
        surname
        forename
        display_name
    """
    translator = None
    translator_rs = select_translator(conn, translator_id)
    if translator_rs is not None:
        # Store the attributes selected from the database.
        id, surname, forename = translator_rs
        translator = {
            "id": id,
            "surname": surname,
            "forename": forename
        }
        
        # Compute the display_name attribute.
        if translator["surname"] is None:
            translator["display_name"] = translator["forename"]
        else:
            translator["display_name"] = translator["forename"] + " " + translator["surname"]
    return translator


def get_translator_data_with_books(conn, translator_id):
    """
    Return None if the translator doesn't exist.
    Otherwise, return a dict containing the translator's data.

    The translator attributes are:
        id
        surname
        forename
        display_name
        books -- a list of book dicts
    """
    translator = get_translator_data(conn, translator_id)
    if translator is not None:
        # Get the books translated by the translator and store the list as the
        # books attribute.
        translator["books"] = []
        book_ids_rs = select_book_ids_for_translator(conn, translator_id)
        for book_id_rs in book_ids_rs:
            (book_id,) = book_id_rs
            book = get_book_data(conn, book_id)
            translator["books"].append(book)
    return translator


def get_translators_for_book(conn, book_id):
    translator_ids_rs = select_translator_ids_for_book(conn, book_id)
    translators = []
    for translator_id_rs in translator_ids_rs:
        (translator_id,) = translator_id_rs
        translator = get_translator_data(conn, translator_id)
        translators.append(translator)
    return translators


########## Display code.

def display_404_not_found():
    html = create_start_html(body_class="about")
    html += create_404_html()
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_about():
    html = create_start_html(body_class="about")
    html += create_about_html()
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_all_authors(conn):
    authors = get_all_authors_data(conn)
    html = create_start_html(body_class="tables")
    html += create_all_authors_table_html(authors)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_all_books(conn):
    books = get_all_books_data(conn)
    html = create_start_html(body_class="tables")
    html += create_all_books_table_html(books)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_author(conn, author_id):
    """
    Display all information about an author including audiobooks
    created or co-created by the author.
    """
    author = get_author_data_with_books(conn, author_id)
    html = create_start_html(body_class="tables")
    if author is None:
        html += f'    <h1>Author ID {author_id} Not Found</h1>\n'
    else:
        html += create_author_html(author)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_book(conn, book_id):
    """
    Given a book ID, query the database for the book's data, create the
    HTML string, and print the Content-Type header and the HTML.

    Report if the book ID is not in the database.
    """
    book = get_book_data(conn, book_id)
    html = create_start_html(body_class="tables")
    if book is None:
        html += f'    <h1>Book ID {book_id} Not Found</h1>\n'
    else:
        html += create_book_html(book)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_narrator(conn, narrator_id):
    narrator = get_narrator_data_with_books(conn, narrator_id)
    html = create_start_html(body_class="tables")
    if narrator is None:
        html += f'    <h1>Narrator ID {narrator_id} Not Found</h1>\n'
    else:
        html += create_narrator_html(narrator)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_summaries(conn):
    summaries = get_summaries_data(conn)
    html = create_start_html(body_class="tables")
    html += create_summaries_html(summaries)
    html += create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html)


def display_translator(conn, translator_id):
    translator = get_translator_data_with_books(conn, translator_id)
    html = create_start_html(body_class="tables")
    if translator is None:
        html += f'    <h1>Translator ID {translator_id} Not Found</h1>\n'
    else:
        html += create_translator_html(translator)
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
        fs = cgi.FieldStorage(keep_blank_values=True)
        if "404" in fs:
            display_404_not_found()
        elif "about" in fs:
            display_about()
        elif "author_id" in fs:
            display_author(conn, fs["author_id"].value)
        elif "authors" in fs:
            display_all_authors(conn)
        elif "book_id" in fs:
            display_book(conn, fs["book_id"].value)
        elif "narrator_id" in fs:
            display_narrator(conn, fs["narrator_id"].value)
        elif "summaries" in fs:
            display_summaries(conn)
        elif "translator_id" in fs:
            display_translator(conn, fs["translator_id"].value)
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
