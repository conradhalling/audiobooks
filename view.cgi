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
            <title>Audiobooks</title>
            <link rel="stylesheet" href="styles.css">
          </head>
          <body>
            <h1>Audiobooks</h1>"""
    print(textwrap.dedent(html_start))


def end_html():
    html_end = """\
          </body>
        </html>"""
    print(textwrap.dedent(html_end))


def print_table():
    # Open a connection.
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
    print('    <table class="adaptive">')
    print('      <thead class="adaptive">')
    print('        <tr class="adaptive">')
    for col_name in ["title", "author", "length", "pub_date", "translator", "narrator"]:
        print(f'          <th class="adaptive">{col_name}</th>')
    print("        </tr>")
    print("      </thead>")
    print('      <tbody class="adaptive">')
    for row in result_set:
        print('        <tr class="adaptive">')
        print(f'          <td class="adaptive">{row[0]}</td>') # title
        print(f'          <td class="adaptive">{row[1]}</td>') # author
        print(f'          <td class="adaptive right">{row[2]}</td>') # length
        print(f'          <td class="adaptive">{row[3] if row[3] is not None else ""}</td>') # pub_date
        print(f'          <td class="adaptive">{row[4] if row[4] is not None else ""}</td>') # translator
        print(f'          <td class="adaptive">{row[5] if row[5] is not None else ""}</td>') # narrator
        print("        </tr>")
    print("      </tbody>")
    print("    </table>")


def main():
    print("Content-Type: text/html\r\n\r\n", end="")
    start_html()
    print_table()
    end_html()

if __name__ == "__main__":
    main()
