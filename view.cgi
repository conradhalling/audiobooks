#!/Users/halto/src/conradhalling/audiobooks/venv310/bin/python3

import os
import sqlite3
import textwrap

from dotenv import load_dotenv
load_dotenv()


def start_html():
    html_start = """\
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
          </head>
          <body>"""
    print(textwrap.dedent(html_start))


def end_html():
    html_end = """\
          </body>
        </html>"""
    print(textwrap.dedent(html_end))


def print_table():
    # Open a connection.
    # db_file = "/Users/halto/src/conradhalling/audiobooks/data/audiobooks.sqlite3"
    db_file = os.environ.get("SQLITE3_DB")
    conn = sqlite3.connect(database=db_file)

    # Enforce foreign key constraints.
    sql_pragma_foreign_keys = "PRAGMA foreign_keys = ON"
    conn.execute(sql_pragma_foreign_keys)

    sql01 = """
        select
            tbl_book.title,
            tbl_author.name as author,
            tbl_book.hours || ':' || printf('%02d', tbl_book.minutes) as length,
            tbl_book.pub_date as publication_date,
            tbl_translator.name as translator,
            tbl_narrator.name as narrator
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
    result_set = conn.execute(sql01)
    print("    <table>")
    print("      <thead>")
    print("        <tr>")
    for col_name in ["title", "author", "length", "pub_date", "translator", "narrator"]:
        print(f"          <th>{col_name}</th>")
    print("        </tr>")
    print("      </thead>")
    print("      <tbody>")
    for row in result_set:
        print("        <tr>")
        for item in row:
            print(f"          <td>{item if item is not None else ''}</td>")
        print("        </tr>")
    print("      </tbody>")
    print("    </table>")


def main():
    print("Content-Type: text/html\r\n\r\n", end="")
    start_html()
    print("    <h1>Audiobooks</h1>")
    print_table()
    end_html()

if __name__ == "__main__":
    main()
