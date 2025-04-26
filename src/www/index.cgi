#!/Users/halto/src/conradhalling/audiobooks/venv310/bin/python3

import cgi
import cgitb
import os
import sys

# Load environment variables from the .env file. The variables are:
#   AUDIOBOOKS_DB           # Full path to the SQLite3 database file
#   AUDIOBOOKS_ENVIRONMENT  # 'PRODUCTION' or 'TEST'
#   AUDIOBOOKS_PYTHONPATH   # Path to the parent directory of the audiobooks package
#   AUDIOBOOKS_WEBDIR       # Full URL path to the directory containing index.cgi
import dotenv
dotenv.load_dotenv()

# Modify sys.path to find the audiobooks package.
sys.path.append(os.environ.get('AUDIOBOOKS_PYTHONPATH'))
import audiobooks


def main():
    """
    Carefully manage exceptions to make sure that the database file is closed.

    Carefully manage HTTP Content-Type headers. Each display function prints
    its own Content-Type header so the application can return HTML, an image,
    CSV, JSON, etc.
    """
    audiobooks.db.connect(db_file=os.environ.get('AUDIOBOOKS_DB'))

    try:
        fs = cgi.FieldStorage(keep_blank_values=True)
        if "404" in fs:
            audiobooks.display.display_404_not_found()
        elif "about" in fs:
            audiobooks.display.display_about()
        elif "author_id" in fs:
            audiobooks.display.display_author(fs["author_id"].value)
        elif "authors" in fs:
            audiobooks.display.display_authors()
        elif "book_id" in fs:
            audiobooks.display.display_book(fs["book_id"].value)
        elif "narrator_id" in fs:
            audiobooks.display.display_narrator(fs["narrator_id"].value)
        elif "summaries" in fs:
            audiobooks.display.display_summary()
        elif "translator_id" in fs:
            audiobooks.display.display_translator(fs["translator_id"].value)
        else:
            audiobooks.display.display_books()

    except Exception as exc:
        # Send the exception to the browser when AUDIOBOOKS_ENVIRONMENT is not
        # PRODUCTION.
        if os.environ.get('AUDIOBOOKS_ENVIRONMENT') != 'PRODUCTION':
            # Send a Content-Type header before printing the exception.
            print("Content-Type: text/html; charset=utf-8\r\n\r\n", end="")
            print(cgitb.html(sys.exc_info()))
        else:
            raise(exc)

    finally:
        audiobooks.db.close()


if __name__ == "__main__":
    main()
