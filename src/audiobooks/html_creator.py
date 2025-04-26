"""
Functions for creating HTML.
"""

import html
import textwrap

from . import config


def create_404_html():
    html_str = """\
    <h1>404: Page Not Found</h1>
    <p>
      Sorry, we've misplaced that URL or it's pointing to something that doesn't
      exist.
    </p>
    """
    return html_str


def create_about_html():
    html_str = """\
    <h1>About 🎧<em>Audio</em>books📚</h1>
    <p>
      I have been tracking the audiobooks I’ve listened to since May, 2008. But
      since my Excel spreadsheet does a poor job of handling multiple authors
      for a book or multiple readings (listenings), I created this tool to make
      it easier to keep track of the audiobooks I’ve listened to.
    </p>
    <p>
      Out of necessity, I wrote this application using Python CGI. This is
      because my shared hosting service supports PHP or Python CGI and not a
      newer protocol such as WSGI (e.g., Flask). Although CGI is dismissed these
      days as obsolete, CGI applications are fairly easy to write.
    </p>
    <p>
      Anyone is welcome to view the data, but at this time I am the only person
      who can add new audiobooks or update existing audiobooks.
    </p>
    <p>
      The source code for this application is available at my
      <a href="https://github.com/conradhalling/audiobooks">GitHub
      repository</a>.
    </p>
    """
    return html_str


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
    html_str = ''
    html_str += '      <h1>Authors</h1>\n'
    html_str += '      <table id="authors">\n'
    html_str += '        <thead>\n'
    html_str += '          <tr>\n'
    html_str += '            <th>Author</th>\n'
    html_str += '            <th>Title</th>\n'
    html_str += '            <th>Rating</th>\n'
    html_str += '            <th class="nowrap">All Authors</th>\n'
    html_str += '            <th>Length</th>\n'
    html_str += '            <th>Acquired</th>\n'
    html_str += '            <th>Status</th>\n'
    html_str += '            <th>Finished</th>\n'
    html_str += '          </tr>\n'
    html_str += '        </thead>\n'
    html_str += '        <tbody>\n'

    index_path = config.get_index_path()
    for author in authors:
        sorted_books = sorted(author["books"], key=lambda book: book["title_sort_key"])
        first_tr = True
        for book in sorted_books:
            html_str += '          <tr>\n'
            if first_tr:
                html_str += f"""            <td class="nowrap"><a href="{index_path}?author_id={html.escape(str(author["id"]))}">{html.escape(author["reverse_name"])}</a></td>\n"""
                first_tr = False
            else:
                html_str += '          <td></td>\n'
            html_str += f"""            <td><a href="{index_path}?book_id={html.escape(str(book["id"]))}">{html.escape(book["title"])}</a></td>\n"""
            html_str += f'            <td class="nowrap">{html.escape(book["rating"])}</td>\n'
            html_str += create_authors_td_html(book["authors"])
            html_str += f'            <td class="right">{html.escape(book["length"])}</td>\n'
            html_str += f'            <td class="nowrap">{html.escape(book["acquisition_date"])}</td>\n'
            html_str += f'            <td>{html.escape(book["status_string"])}</td>\n'
            html_str += f'            <td class="nowrap">{html.escape(book["finish_date_string"])}</td>\n'
            html_str += '          </tr>\n'
    html_str += '        </tbody>\n'
    html_str += '      </table>\n'
    return html_str


def create_all_books_table_html(books):
    """
    Create the HTML for all books.
    """
    html_str =  '      <h1>Audiobooks</h1>\n'
    html_str += '      <div class="filters">\n'
    html_str += '        <strong>Filter by Status:</strong>\n'
    html_str += '        <input type="checkbox" id="new" title="Click this checkbox to toggle the visibility of new audiobooks." checked>\n'
    html_str += '        <label for="new" title="Click this checkbox to toggle the visibility of new audiobooks.">New</label>\n'
    html_str += '        <input type="checkbox" id="started" title="Click this checkbox to toggle the visibility of started audiobooks." checked>\n'
    html_str += '        <label for="started" title="Click this checkbox to toggle the visibility of started audiobooks.">Started</label>\n'
    html_str += '        <input type="checkbox" id="finished" title="Click this checkbox to toggle the visibility of finished audiobooks." checked>\n'
    html_str += '        <label for="finished" title="Click this checkbox to toggle the visibility of finished audiobooks.">Finished</label>\n'
    html_str += '      </div>\n'
    html_str += create_sortable_books_table_html(books, filterable=True)
    return html_str


def create_author_html(author):
    """
    author is a dict containing information about the author and the books the
    author has created.
    """
    html_str = ""
    html_str += f'    <h1>Audiobooks Created by {html.escape(author["display_name"])}</h1>\n'
    html_str += create_sortable_books_table_html(author["books"])
    return html_str


def create_authors_td_html(authors):
    """
    authors is a list of dicts containing author data.
    """
    index_path = config.get_index_path()
    author_strings = []
    first_author = True
    for author in authors:
        if first_author:
            # The sort key comes from the name of the first author.
            author_name_sort_key = author["name_sort_key"]
            first_author = False
        author_string = f'<a href="{index_path}?author_id={html.escape(str(author["id"]))}">{html.escape(author["reverse_name"])}</a>'
        author_strings.append(author_string)
    html_str = f'            <td data-sortkey="{html.escape(author_name_sort_key)}" class="nowrap">{"<br>".join(author_strings)}</td>\n'
    return html_str


def create_book_html(book):
    """
    book is a dict from which all information about an audiobook can
    be extracted.
    """
    index_path = config.get_index_path()

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
        author_html_string = f"""<a href="{index_path}?author_id={html.escape(str(author['id']))}">{html.escape(author['display_name'])}</a>"""
        author_html_strings.append(author_html_string)
        author_strings.append(author["display_name"])

    translator_html_strings = []
    for translator in book["translators"]:
        translator_html_string = f"""<a href="{index_path}?translator_id={html.escape(str(translator['id']))}">{html.escape(translator['display_name'])}</a>"""
        translator_html_strings.append(translator_html_string)

    narrator_html_strings = []
    for narrator in book["narrators"]:
        narrator_html_string = f"""<a href="{index_path}?narrator_id={html.escape(str(narrator['id']))}">{html.escape(narrator['display_name'])}</a>"""
        narrator_html_strings.append(narrator_html_string)

    # Build the by authors string for the header.
    # This algorithm works, but there must be an easier way.
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
    html_str = ''
    html_str += f'      <h1><cite>{html.escape(book["title"])}</cite><br>by {html.escape(by_authors_string)}</h1>\n'
    html_str += '      <h2>Audiobook Information</h2>\n'
    html_str += '      <table>\n'
    html_str += '        <tbody class="vertical">\n'

    # Title
    html_str += '          <tr>\n'
    html_str += '            <th class="vertical">Title</th>\n'
    html_str += f'            <td><cite>{html.escape(book["title"])}</cite></td>\n'
    html_str += '          </tr>\n'

    # Authors
    html_str += '          <tr>\n'
    html_str += '            <th class="vertical">Author{}</th>\n'.format(
        "s" if len(author_strings) > 1 else "")
    html_str += f'            <td>{"<br>".join(author_html_strings)}</td>\n'
    html_str += '          </tr>\n'

    # Length
    html_str += '          <tr>\n'
    html_str += '            <th class="vertical nowrap">Length (hr:min)</th>\n'
    html_str += f'            <td>{html.escape(book["length"])}</td>\n'
    html_str += '          </tr>\n'

    # Translators
    if len(translator_html_strings) > 0:
        html_str += '          <tr>\n'
        html_str += '            <th class="vertical">Translator{}</th>\n'.format(
            "s" if len(translator_html_strings) > 1 else "")
        html_str += f'            <td>{"<br>".join(translator_html_strings)}</td>\n'
        html_str += '          </tr>\n'

    # Narrators
    html_str += '          <tr>\n'
    html_str += '            <th class="vertical">Narrator{}</th>\n'.format(
        "s" if len(narrator_html_strings) != 1 else "")
    html_str += f'            <td>{"<br>".join(narrator_html_strings)}</td>\n'
    html_str += '          </tr>\n'

    # Book Pub. Date
    if book_pub_date:
        html_str += '          <tr>\n'
        html_str += '            <th class="vertical nowrap">Book Pub. Date</th>\n'
        html_str += f'            <td>{html.escape(book_pub_date)}</td>\n'
        html_str += '          </tr>\n'

    # Audio Pub. Date
    if audio_pub_date:
        html_str += '          <tr>\n'
        html_str += '            <th class="vertical nowrap">Audio Pub. Date</th>\n'
        html_str += f'            <td>{html.escape(audio_pub_date)}</td>\n'
        html_str += '          </tr>\n'

    # Acquired By
    html_str += '          <tr>\n'
    html_str += '            <th class="vertical nowrap">Acquired By</th>\n'
    html_str += f'            <td>{html.escape(book["acquisition"]["username"])}</td>\n'
    html_str += '          </tr>\n'

    # Vendor
    html_str += '          <tr>\n'
    html_str += '            <th class="vertical">Vendor</th>\n'
    html_str += f'            <td>{html.escape(book["acquisition"]["vendor_name"])}</td>\n'
    html_str += '          </tr>\n'

    # Acquisition Type
    html_str += '          <tr>\n'
    html_str += '            <th class="vertical nowrap">Acquisition Type</th>\n'
    html_str += f'            <td>{html.escape(book["acquisition"]["acquisition_type"])}</td>\n'
    html_str += '          </tr>\n'

    # Acquisition Date
    html_str += '          <tr>\n'
    html_str += '            <th class="vertical nowrap">Acquisition Date</th>\n'
    html_str += f'            <td>{html.escape(book["acquisition"]["acquisition_date"])}</td>\n'
    html_str += '          </tr>\n'

    # Discontinued
    if discontinued:
        html_str += '          <tr>\n'
        html_str += '            <th class="vertical">Discontinued</th>\n'
        html_str += f'            <td>{html.escape(discontinued)}</td>\n'
        html_str += '          </tr>\n'

    # Audible Credits
    if book["acquisition"]["audible_credits"] is not None:
        html_str += '          <tr>\n'
        html_str += '            <th class="vertical nowrap">Audible Credits</th>\n'
        html_str += f'            <td>{html.escape(str(book["acquisition"]["audible_credits"]))}</td>\n'
        html_str += '          </tr>\n'

    # Price (Dollars)
    if price_in_dollars:
        html_str += '          <tr>\n'
        html_str += '            <th class="vertical">Price</th>\n'
        html_str += f'            <td>{html.escape(price_in_dollars)}</td>\n'
        html_str += '          </tr>\n'

    html_str += '        </tbody>\n'
    html_str += '      </table>\n'

    # Listener Notes
    html_str += '      <h2>Listener Notes</h2>\n'
    html_str += '      <table>\n'
    html_str += '        <thead>\n'
    html_str += '          <tr>\n'
    headers = ('Listener', 'Status', 'Finished', "Rating", "Comments")
    for header in headers:
        html_str += f'            <th>{html.escape(header)}</th>\n'
    html_str += '          </tr>\n'
    html_str += '        </thead>\n'
    html_str += '        <tbody>\n'
    for note in book["notes"]:
        html_str += '          <tr>\n'
        html_str += f'            <td>{html.escape(note["username"])}</td>\n'
        html_str += f'            <td>{html.escape("" if note["status"] is None else note["status"])}</td>\n'
        html_str += f'            <td class="nowrap">{html.escape("" if note["finish_date"] is None else note["finish_date"])}</td>\n'
        rating = ""
        if note["rating_stars"] is not None:
            rating = str(note["rating_stars"]) + " " + note["rating_description"]
        html_str += f'            <td class="nowrap">{html.escape(rating)}</td>\n'
        html_str += f'            <td>{html.escape("" if note["comments"] is None else note["comments"])}</td>\n'
        html_str += '          </tr>\n'
    html_str += '      </table>\n'
    return html_str


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
    html_str = ""
    html_str += f'    <h1>Audiobooks Narrated by {html.escape(narrator["display_name"])}</h1>\n'
    html_str += create_sortable_books_table_html(narrator["books"])
    return html_str


def create_sortable_books_table_html(books, filterable=False):
    """
    The all books table is filterable; the books table associated with an
    author, translator, or narrator is not filterable.
    """
    index_path = config.get_index_path()

    th_tool_tip = "Click this header to sort the table by the values in this column."
    html_str = ''
    if filterable:
        html_str += '      <table id="audiobooks" class="filterable">\n'
    else:
        html_str += '      <table id="audiobooks">\n'
    html_str += '        <thead>\n'
    html_str += '          <tr>\n'

    # Since the table is sorted by title, put the up arrow symbol in the
    # span element.
    html_str += f'            <th class="sortable nowrap" title="{th_tool_tip}">Title <span>⭡</span></th>\n'
    html_str += f'            <th class="sortable nowrap" title="{th_tool_tip}">Authors <span>⭥</span></th>\n'
    html_str += f'            <th class="sortable nowrap" title="{th_tool_tip}">Rating <span>⭥</span></th>\n'
    html_str += f'            <th class="sortable nowrap" title="{th_tool_tip}">Length <span>⭥</span></th>\n'
    html_str += f'            <th class="sortable nowrap" title="{th_tool_tip}">Acquired <span>⭥</span></th>\n'
    html_str += f'            <th class="sortable nowrap" title="{th_tool_tip}">Status <span>⭥</span></th>\n'
    html_str += f'            <th class="sortable nowrap" title="{th_tool_tip}">Finished <span>⭥</span></th>\n'
    html_str += '          </tr>\n'
    html_str += '        </thead>\n'
    html_str += '        <tbody>\n'

    # Sort by the title sort key.
    sorted_books = sorted(books, key=lambda book: book["title_sort_key"])

    # Get the book attributes for the table.
    for book in sorted_books:
        # Create table rows for all books, reporting only the first finished date.
        html_str += f"""          <tr class="{html.escape(book['notes'][0]['status'].lower())}">\n"""
        html_str += f"""            <td data-sortkey="{html.escape(book['title_sort_key'])}"><a href="{index_path}?book_id={html.escape(str(book['id']))}">{html.escape(book['title'])}</a></td>\n"""
        html_str += create_authors_td_html(book["authors"])
        html_str += f"""            <td class="nowrap">{html.escape(book['rating'])}</td>\n"""
        html_str += f"""            <td data-sortkey="{html.escape(str(book['length_sort_key']))}" class="right">{html.escape(book["length"])}</td>\n"""
        html_str += f"""            <td>{html.escape(book["acquisition"]["acquisition_date"])}</td>\n"""
        html_str += f"""            <td>{html.escape(book["notes"][0]["status"])}</td>\n"""
        html_str += f'            <td>{html.escape(book["finish_date_string"])}</td>\n'
        html_str += '          </tr>\n'

    html_str += '        </tbody>\n'
    html_str += '      </table>\n'
    return html_str


def create_start_html(body_class="tables"):
    """
    body_class is "tables" when data tables are shown, in which case the
    body's margins are reduced to the minimum in a narrow viewport.

    body_class is "about" when the about page is displayed; there is
    sufficient room on the page that the margins can remain the same.

    This function requires the AUDIOBOOKS_WEBDIR environment variable
    for determing the locations of styles.css and js/main.js.
    """
    index_path = config.get_index_path()
    js_dir_path = config.get_js_dir_path()
    styles_path = config.get_styles_path()
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
                  <li><a href="{index_path}?summaries">Summary</a></li>
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


def create_summary_html(summary):
    html_str = '      <h1>Summary</h1>\n'
    html_str += '      <h2>Annual Totals</h2>\n'
    html_str += '      <table>\n'
    html_str += '        <caption>Number of audiobooks acquired and finished each year</caption>\n'
    html_str += '        <thead>\n'
    html_str += '          <tr>\n'
    html_str += '            <th>Year</th>\n'
    html_str += '            <th>Acquired</th>\n'
    html_str += '            <th>Finished</th>\n'
    html_str += '          </tr>\n'
    html_str += '        </thead>\n'
    html_str += '        <tbody>\n'
    for row in summary["counts_by_year"]:
        html_str += '        <tr>\n'
        html_str += f'          <td class="right">{html.escape(str(row["year"]))}</td>\n'
        html_str += f'          <td class="right">{html.escape(str(row["acquired"]))}</td>\n'
        html_str += f'          <td class="right">{html.escape(str(row["finished"]))}</td>\n'
        html_str += f'        </tr>\n'
    html_str += '        </tbody>\n'
    html_str += '      </table>\n'

    html_str += '      <h2>Grand Totals</h2>\n'
    html_str += '      <table>\n'
    html_str += '        <caption>All Audiobooks Finished includes multiple listens of audiobooks</caption>'
    html_str += '        <tbody>\n'
    html_str += '          <tr>\n'
    html_str += '            <th>Audiobooks Acquired</th>\n'
    html_str += f'            <td class="right">{html.escape(str(summary["totals"]["acquired"]))}</td>\n'
    html_str += '          </tr>\n'
    html_str += '          <tr>\n'
    html_str += '            <th>Distinct Audiobooks Finished</th>\n'
    html_str += f'            <td class="right">{html.escape(str(summary["totals"]["distinct_finished"]))}</td>\n'
    html_str += '          </tr>\n'
    html_str += '          <tr>\n'
    html_str += '            <th>Audiobooks Not Finished</th>\n'
    html_str += f'            <td class="right">{html.escape(str(summary["totals"]["not_finished"]))}</td>\n'
    html_str += '          </tr>\n'
    html_str += '          <tr>\n'
    html_str += '            <th>All Audiobooks Finished</th>\n'
    html_str += f'            <td class="right">{html.escape(str(summary["totals"]["all_finished"]))}</td>\n'
    html_str += '          </tr>\n'
    html_str += '        </tbody>\n'
    html_str += '      </table>\n'
    return html_str


def create_translator_html(translator):
    """
    translator is a dict containing information about the translator and the books the
    translator has translated.
    """
    html_str = ""
    html_str += f'    <h1>Audiobooks Translated by {html.escape(translator["display_name"])}</h1>\n'
    html_str += create_sortable_books_table_html(translator["books"])
    return html_str
