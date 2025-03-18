#!/Users/halto/src/conradhalling/audiobooks/venv310/bin/python3

import cgi
import cgitb
cgitb.enable()
import os
import sqlite3
import textwrap

from dotenv import load_dotenv
load_dotenv()


def get_all_books_data():
    # Open a connection.
    db_file = os.environ.get("SQLITE3_DB")
    conn = sqlite3.connect(database=db_file)

    # Enforce foreign key constraints.
    sql_pragma_foreign_keys = "PRAGMA foreign_keys = ON"
    conn.execute(sql_pragma_foreign_keys)

    sql_select_books = """
        select
            tbl_book.title,
            tbl_author.name as author,
            tbl_book.hours || ':' || printf('%02d', tbl_book.minutes) as length,
            tbl_book.book_pub_date as publication_date,
            tbl_translator.name as translator,
            tbl_narrator.name as narrator,
            tbl_book.id,
            tbl_author.id
        from
            tbl_book
            left outer join tbl_book_author
                on tbl_book.id = tbl_book_author.book_id
            left outer join tbl_author
                on tbl_book_author.author_id = tbl_author.id
            left outer join tbl_book_translator
                on tbl_book.id = tbl_book_translator.book_id
            left outer join tbl_translator
                on tbl_book_translator.translator_id = tbl_translator.id
            left outer join tbl_book_narrator
                on tbl_book.id = tbl_book_narrator.book_id
            left outer join tbl_narrator
                on tbl_book_narrator.narrator_id = tbl_narrator.id
    """
    result_set = conn.execute(sql_select_books)
    return result_set


def start_html():
    html_start = """\
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Audiobooks</title>
            <link rel="stylesheet" href="styles.css">
          </head>
          <body>"""
    print(textwrap.dedent(html_start))


def end_html():
    html_end = """\
          </body>
        </html>"""
    print(textwrap.dedent(html_end))


def print_all_books_table(result_set):
    print('    <h1 class="adaptive">All Audiobooks</h1>')
    print('    <table class="adaptive">')
    print('      <thead class="adaptive">')
    print('        <tr class="adaptive">')
    for col_name in ["title", "author", "length", "pub_date", "translator", "narrator"]:
        print(f'          <th class="adaptive">{col_name}</th>')
    print("        </tr>")
    print("      </thead>")
    print('      <tbody class="adaptive">')
    for row in result_set:
        (title, author, length, pub_date, translator, narrator, book_id, author_id) = row
        print('        <tr class="adaptive">')
        print(f'          <td class="adaptive"><a class="adaptive" href="?book_id={book_id}">{title}</a></td>')
        print(f'          <td class="adaptive"><a class="adaptive" href="?author_id={author_id}">{author}</a></td>')
        print(f'          <td class="adaptive right">{length}</td>')
        print(f'          <td class="adaptive">{pub_date if pub_date is not None else ""}</td>')
        print(f'          <td class="adaptive">{translator if translator is not None else ""}</td>')
        print(f'          <td class="adaptive">{narrator if narrator is not None else ""}</td>')
        print("        </tr>")
    print("      </tbody>")
    print("    </table>")


def display_all_books():
    result_set = get_all_books_data()
    start_html()
    print_all_books_table(result_set)
    end_html()


def display_author(author_id):
    start_html()
    print(f'    <h1 class="adaptive">Author {author_id}</h1>')
    print(f'    <p class="adaptive">{author_id}</p>')


def display_book(book_id):
    start_html()
    print(f'    <h1 class="adaptive">Book {book_id}</h1>')
    print(f'    <p class="adaptive">{book_id}</p>')


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
