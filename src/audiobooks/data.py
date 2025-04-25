"""
Functions that return data as dicts and lists.
"""

from . import db


def get_acquisition_for_book(book_id):
    """
    Given a book's ID, return a dict containing the acquisition's attributes.

    The acquisition's attributes are:
        id
        username
        vendor_name
        acquisition_type
        acquisition_date
        discontinued
        audible_credits
        price_in_cents

    Return None if the acquisition is not found.
    """
    row = db.acquisition.select_acquisition_for_book(book_id)
    acquisition = None
    if row is not None:
        (id, username, vendor_name, acquisition_type, acquisition_date,
            discontinued, audible_credits, price_in_cents) = row
        acquisition = {
            "id": id,
            "username": username,
            "vendor_name": vendor_name,
            "acquisition_type": acquisition_type,
            "acquisition_date": acquisition_date,
            "discontinued": discontinued,
            "audible_credits": audible_credits,
            "price_in_cents": price_in_cents,
        }
    return acquisition


def get_author(author_id):
    """
    Return a dict containing the author's attributes, excluding the books
    attribute.

    The author's attributes are:
        id
        surname
        forename
        display_name  -- forename + " " + surname
        reverse_name  -- surname + ", " + forename
        name_sort_key -- (surname + " " + forename).upper()

    Return None if the author doesn't exist.
    """
    author = None
    row = db.author.select(author_id)
    if row is not None:
        id, surname, forename = row
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


def get_author_with_books(author_id):
    """
    Given an author's ID, return a dict containing the author's attributes
    including the books written by the author.

    The author's attributes are:
        id
        surname
        forename
        display_name
        reverse_name
        name_sort_key
        books -- a list of book dicts

    Return None if the author doesn't exist.
    """
    author = get_author(author_id)
    if author is not None:
        # Get the books written by the author and store the list as the
        # books attribute.
        author["books"] = []
        rows = db.book.select_ids_for_author(author_id)
        for row in rows:
            (book_id,) = row
            book = get_book(book_id)
            author["books"].append(book)
    return author


def get_authors_with_books():
    """
    Return a list of sorted author dicts, where the author attributes include
    the books written by the author and the list is sorted by the
    author["name_sort_key"] attribute.
    """
    authors = []
    rows = db.author.select_ids()
    for row in rows:
        (author_id,) = row
        author = get_author_with_books(author_id)
        authors.append(author)
    sorted_authors = sorted(authors, key=lambda author: author["name_sort_key"])
    return sorted_authors


def get_authors_for_book(book_id):
    """
    Given a book's ID, return a list of authors of the book.

    Return an empty list if no authors are found.

    For each author, do not include the books attribute, since that would cause
    an infinite loop since each book attribute has an authors attribute.
    """
    rows = db.author.select_ids_for_book(book_id)
    authors = []
    for row in rows:
        (author_id,) = row
        author = get_author(author_id)
        authors.append(author)
    return authors


def get_book(book_id):
    """
    Given a book's ID, return a dict containing the book's attributes.

    The book's attributes are:
        id
        title
        book_pub_date
        audio_pub_date
        hours
        minutes
        authors -- a list of author dicts
        translators -- a list of translator dicts
        narrators -- a list of narrator dicts
        acquisition
        notes -- a list of note dicts
        title_sort_key
        length_sort_key
        length
        rating
        finish_date_string
        status_string
        acquisition_date

    Return None if the book's ID is not in the database.
    """
    row = db.book.select_book(book_id)
    if row is None:
        return None

    (id, title, book_pub_date, audio_pub_date, hours, minutes,) = row
    book = {
        "id": id,
        "title": title,
        "book_pub_date": book_pub_date,
        "audio_pub_date": audio_pub_date,
        "hours": hours,
        "minutes": minutes,
    }
    book["authors"] = get_authors_for_book(book_id)
    book["translators"] = get_translators_for_book(book_id)
    book["narrators"] = get_narrators_for_book(book_id)

    # Acquisition
    acquisition = get_acquisition_for_book(book_id)
    book["acquisition"] = acquisition

    # Notes for book.
    notes = get_notes_for_book(book_id)
    book["notes"] = notes

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


def get_books():
    """
    Return a list of all books, where the list is sorted by the
    book["title_sort_key"] attribute.
    """
    books = []
    rows = db.book.select_ids()
    for row in rows:
        (book_id,) = row
        book = get_book(book_id)
        books.append(book)
    sorted_books = sorted(books, key=lambda book: book["title_sort_key"])
    return sorted_books


def get_narrator(narrator_id):
    """
    Given a narrator's ID, return a dict containing the narrator's attributes
    except the books attribute.

    The narrator's attributes are:
        id
        surname
        forename
        display_name

    Return None if the narrator doesn't exist.
    """
    narrator = None
    row = db.narrator.select_narrator(narrator_id)
    if row is not None:
        # Store the attributes selected from the database.
        id, surname, forename = row
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


def get_narrator_with_books(narrator_id):
    """
    Given a narrator's ID, return a dict containing the narrator's attributes
    including the books narrated by the narrator.

    The narrator's attributes are:
        id
        surname
        forename
        display_name
        books -- a list of book dicts

    Return None if the narrator doesn't exist.
    """
    narrator = get_narrator(narrator_id)
    if narrator is not None:
        # Get the books narrated by the narrator and store the list as the
        # books attribute.
        narrator["books"] = []
        rows = db.book.select_ids_for_narrator(narrator_id)
        for row in rows:
            (book_id,) = row
            book = get_book(book_id)
            narrator["books"].append(book)
    return narrator


def get_narrators_for_book(book_id):
    """
    Given a book's ID, return a list of dicts containing the attributes of
    the narrators of the book.

    Return an empty list if no narrators are found.
    """
    rows = db.narrator.select_ids_for_book(book_id)
    narrators = []
    for row in rows:
        (narrator_id,) = row
        narrator = get_narrator(narrator_id)
        narrators.append(narrator)
    return narrators


def get_note_for_book(book_id):
    pass


def get_notes_for_book(book_id):
    """
    Given a book's ID, return a list of dicts containing the note attributes.

    The note's attributes are:
        id
        username
        status
        finish_date
        rating_stars
        rating_description
        comments

    Return an empty list if no notes are found.
    """
    rows = db.note.select_notes_for_book(book_id)
    notes = []
    for row in rows:
        (id, username, status, finish_date, rating_stars, rating_description,
         comments) = row
        note = {
            "id": id,
            "username": username,
            "status": status,
            "finish_date": finish_date,
            "rating_stars": rating_stars,
            "rating_description": rating_description,
            "comments": comments,
        }
        notes.append(note)
    return notes


def get_rating(note):
    """
    From a note dict, return a rating string that is a combination of the
    rating_stars and rating_description values. Return an empty string if these
    are None.
    """
    rating = ""
    if note["rating_stars"] is not None:
        rating = str(note["rating_stars"]) + " " + note["rating_description"]
    return rating


def get_summaries():
    """
    Return a dict containing summaries attributes.

    The attributes are:
        counts_by_year: list of dicts:
            year
            acquired
            finished
        totals: dict:
            acquired
            distinct_finished
            not_finished
            all_finished
    """
    summaries = {}
    # year_counts is a list of dicts with keys "year", "acquired", and
    # finished" and values the year, the number of books acquired that
    # year, and the number of books finished that year.
    cby_rows = db.counts.select_counts_by_year()
    counts_by_year = []
    for cby_row in cby_rows:
        (year, acquired, finished) = cby_row
        year_dict = {
            "year": year,
            "acquired": acquired,
            "finished": finished,
        }
        counts_by_year.append(year_dict)
    summaries["counts_by_year"] = counts_by_year

    # totals is a dict containing acquired, distinct_finished, not_finished,
    # and all_finished totals.
    tba_row = db.counts.select_total_books_acquired()
    total_books_acquired = 0
    if tba_row is not None:
        total_books_acquired = tba_row[0]

    tdbf_row = db.counts.select_total_distinct_books_finished()
    total_distinct_books_finished = 0
    if tdbf_row is not None:
        total_distinct_books_finished = tdbf_row[0]

    total_books_unfinished = 0
    tbu_row = db.counts.select_total_books_unfinished()
    if tbu_row is not None:
        total_books_unfinished = tbu_row[0]

    total_books_finished = 0
    tbf_row = db.counts.select_total_books_finished()
    if tbf_row is not None:
        total_books_finished = tbf_row[0]

    totals = {
        "acquired": total_books_acquired,
        "distinct_finished": total_distinct_books_finished,
        "not_finished": total_books_unfinished,
        "all_finished": total_books_finished,
    }
    summaries["totals"] = totals
    return summaries


def get_translator(translator_id):
    """
    Return a dict containing the translator's attributes, excluding the books
    attribute.

    The translator's attributes are:
        id
        surname
        forename
        display_name  -- forename + " " + surname

    Return None if the translator doesn't exist.
    """
    translator = None
    row = db.translator.select_translator(translator_id)
    if row is not None:
        # Store the attributes selected from the database.
        id, surname, forename = row
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


def get_translator_with_books(translator_id):
    """
    Given a translator's ID, return a dict containing the translator's
    attributes including the books translated by the translator.

    The translator's attributes are:
        id
        surname
        forename
        display_name
        books -- a list of book dicts

    Return None if the translator doesn't exist.
    """
    translator = get_translator(translator_id)
    if translator is not None:
        translator["books"] = []
        rows = db.book.select_ids_for_translator(translator_id)
        for row in rows:
            (book_id,) = row
            book = get_book(book_id)
            translator["books"].append(book)
    return translator


def get_translators_for_book(book_id):
    """
    Given a book's ID, return a list of dicts containing the attributes of
    the translators of the book.

    Return an empty list if no translators are found.
    """
    rows = db.translator.select_ids_for_book(book_id)
    translators = []
    for row in rows:
        (translator_id,) = row
        translator = get_translator(translator_id)
        translators.append(translator)
    return translators


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
