"""
Functions for displaying information in web pages.
"""

import html

from . import data
from . import create_html


def display_404_not_found():
    html_str = create_html.create_start_html(body_class="about")
    html_str += create_html.create_404_html()
    html_str += create_html.create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html_str)


def display_about():
    html_str = create_html.create_start_html(body_class="about")
    html_str += create_html.create_about_html()
    html_str += create_html.create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html_str)


def display_author(author_id):
    """
    Display all information about an author including audiobooks created or
    co-created by the author.

    author_id must be an int > 0.
    """
    html_str = create_html.create_start_html(body_class="tables")
    if str.isdigit(author_id) and str.isascii(author_id) and int(author_id) > 0:
        author = data.get_author_with_books(author_id)
        if author is None:
            html_str += f'    <h1>Author ID "{html.escape(author_id)}" Not Found</h1>\n'
        else:
            html_str += create_html.create_author_html(author)
    else:
        html_str += f'    <h1>Invalid author ID "{html.escape(author_id)}"</h1>\n'
    html_str += create_html.create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html_str)


def display_authors():
    """
    Display information about all authors.
    """
    authors = data.get_authors_with_books()
    html_str = create_html.create_start_html(body_class="tables")
    html_str += create_html.create_all_authors_table_html(authors)
    html_str += create_html.create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html_str)


def display_book(book_id):
    """
    Given a book ID, display information about the book.
    """
    html_str = create_html.create_start_html(body_class="tables")
    if str.isdigit(book_id) and str.isascii(book_id) and int(book_id) > 0:
        book = data.get_book(book_id)
        if book is None:
            html_str += f'    <h1>Book ID "{html.escape(book_id)}" Not Found</h1>\n'
        else:
            html_str += create_html.create_book_html(book)
    else:
        html_str += f'    <h1>Invalid book ID "{html.escape(book_id)}"</h1>\n'
    html_str += create_html.create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html_str)


def display_books():
    """
    Display information about all books.
    """
    books = data.get_books()
    html_str = create_html.create_start_html(body_class="tables")
    html_str += create_html.create_all_books_table_html(books)
    html_str += create_html.create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html_str)


def display_narrator(narrator_id):
    """
    Given a narrator's ID, query the database for the narrator's data, create the
    HTML string, and print the Content-Type header and the HTML.

    narrator_id must be an int > 0.
    """
    html_str = create_html.create_start_html(body_class="tables")
    if str.isdigit(narrator_id) and str.isascii(narrator_id) and int(narrator_id) > 0:
        narrator = data.get_narrator_with_books(narrator_id)
        if narrator is None:
            html_str += f'    <h1>Narrator ID {html.escape(narrator_id)} Not Found</h1>\n'
        else:
            html_str += create_html.create_narrator_html(narrator)
    else:
        html_str += f'    <h1>Invalid narrator ID "{html.escape(narrator_id)}"</h1>\n'
    html_str += create_html.create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html_str)


def display_summaries():
    summaries = data.get_summaries()
    html_str = create_html.create_start_html(body_class="tables")
    html_str += create_html.create_summaries_html(summaries)
    html_str += create_html.create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html_str)


def display_translator(translator_id):
    """
    Given a translator's ID, query the database for the translator's data, create
    the HTML string, and print the Content-Type header and the HTML.

    translator_id must be an int > 0.
    """
    html_str = create_html.create_start_html(body_class="tables")
    if str.isdigit(translator_id) and str.isascii(translator_id) and int(translator_id) > 0:
        translator = data.get_translator_with_books(translator_id)
        if translator is None:
            html_str += f'    <h1>Translator ID "{html.escape(translator_id)}" Not Found</h1>\n'
        else:
            html_str += create_html.create_translator_html(translator)
    else:
        html_str += f'    <h1>Invalid translator ID "{html.escape(translator_id)}"</h1>\n'
    html_str += create_html.create_end_html()
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
    print(html_str)
