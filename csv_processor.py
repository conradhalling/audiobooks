"""
CSV file processing code.
"""

import csv
import logging
logger = logging.getLogger(__name__)

import db


def convert_price(csv_price):
    """
    Convert the CSV price by removing "$" and "." characters and expressing the
    result in cents. For example, this converts "$8.95" to 895. If the CSV price
    is empty, return None.
    """
    price = None
    if csv_price != "":
        temp_price = ""
        for char in csv_price:
            if char != "$" and char != ".":
                temp_price += char
        if temp_price != "":
            price = int(temp_price)
    return price


def load_csv_data(csv_file, vendor):
    """
    Given the CSV data file for the given vendor, parse the data fields
    and load the data into the database.
    """
    vendor_id = db.vendor.save(vendor)

    with open(csv_file, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        # Skip the header line.
        row = next(csv_reader)
        for csv_row in csv_reader:
            (
                csv_title,
                csv_authors,
                csv_translators,
                csv_narrators,
                csv_pub_date,
                csv_hours,
                csv_minutes,
                csv_acquisition_date,
                csv_status,
                csv_finished_date,
                csv_acquisition_type,
                csv_audible_credits,
                csv_price,
                csv_rating,
                csv_discontinued,
                csv_reread,
                csv_comments,
            ) = csv_row
            logger.debug(f"csv_authors: '{csv_authors}'")
            author_ids = save_authors(csv_authors)

            logger.debug(f"csv_translators: '{csv_translators}'")
            translator_ids = save_translators(csv_translators)

            logger.debug(f"csv_narrators: '{csv_narrators}'")
            narrator_ids = save_narrators(csv_narrators)

            logger.debug(f"csv_title: '{csv_title}'")
            logger.debug(f"csv_pub_date: '{csv_pub_date}'")
            logger.debug(f"hours: {csv_hours}")
            logger.debug(f"minutes: {csv_minutes}")
            audio_pub_date = ""
            book_id = save_book(csv_title, csv_pub_date, audio_pub_date, csv_hours, csv_minutes, csv_discontinued)

            for author_id in author_ids:
                db.book_author.save(book_id, author_id)
            
            for translator_id in translator_ids:
                db.book_translator.save(book_id, translator_id)
            
            for narrator_id in narrator_ids:
                db.book_narrator.save(book_id, narrator_id)
            
            book_acquisiton_id = save_book_acquisition(
                book_id, 
                vendor_id, 
                vendor, 
                csv_acquisition_type, 
                csv_acquisition_date, 
                csv_audible_credits, 
                csv_price,
            )
            
            note_id = save_note(
                book_id,
                csv_reread,
                csv_status,
                csv_finished_date,
                csv_rating,
                csv_comments,
            )


def save_authors(authors_str):
    """
    Multiple authors are separated by "&".
    No effort is made at this time to break author names into
    first name, middle name, and last name.
    """
    logger.debug(f"authors_str: '{authors_str}'")
    authors = authors_str.split(sep="&")
    logger.debug(f"authors: {authors}")
    author_ids = []
    for author in authors:
        author = author.strip()
        if author != "":
            author_id = db.author.save(author)
            author_ids.append(author_id)
    logger.debug(f"author ids: {author_ids}")
    return author_ids


def save_book(title, book_pub_date, audio_pub_date, hours, minutes, discontinued):
    logger.debug(f"title: '{title}'")
    logger.debug(f"book_pub_date: '{book_pub_date}'")
    logger.debug(f"audio_pub_date: '{audio_pub_date}'")
    logger.debug(f"hours: {hours}")
    logger.debug(f"minutes: {minutes}")
    if book_pub_date == "":
        book_pub_date = None
    if audio_pub_date == "":
        audio_pub_date = None
    if discontinued == "":
        discontinued = None
    book_id = db.book.save(title, book_pub_date, audio_pub_date, hours, minutes, discontinued)
    logger.debug(f"book_id: {book_id}")
    return book_id


def save_book_acquisition(
        book_id,
        vendor_id, 
        vendor, 
        csv_acquisition_type, 
        csv_acquisition_date, 
        csv_audible_credits, 
        csv_price):
    """
    Convert book acquisition attributes and save the book acquisition.
    """
    if vendor == "audible.com":
        acquisition_types = {
            "Credit": "vendor credit",
            "Extra": "charge",
            "Free": "no charge",
            "Plus": "member benefit",
            "Podcast": "podcast"
        }
    csv_acquisition_type = csv_acquisition_type.strip()
    if csv_acquisition_type in acquisition_types:
        acquisition_type = acquisition_types[csv_acquisition_type]
    else:
        raise ValueError(f"vendor '{vendor}' csv_acquisition_type '{csv_acquisition_type}' not handled")
    acquisition_type_id = db.acquisition_type.save(acquisition_type)

    if csv_acquisition_date == "":
        raise ValueError("csv_acquistion_date must not be empty")
    
    audible_credits = None
    if csv_audible_credits != "":
        audible_credits = csv_audible_credits
    
    price = convert_price(csv_price)

    db.book_acquisition.save(
        book_id, vendor_id, acquisition_type_id, csv_acquisition_date,
        audible_credits, price)


def save_narrators(narrators_str):
    """
    Multiple narrators are separated by "&".
    No effort is made at this time to break narrator names into
    first name, middle name, and last name.
    """
    logger.debug(f"narrators_str: '{narrators_str}'")
    narrators = narrators_str.split(sep="&")
    logger.debug(f"narrators: {narrators}")
    narrator_ids = []
    for narrator in narrators:
        narrator = narrator.strip()
        if narrator != "":
            narrator_id = db.narrator.save(narrator)
            narrator_ids.append(narrator_id)
    logger.debug(f"narrator ids: {narrator_ids}")
    return narrator_ids


def save_note(book_id, csv_reread, csv_status, csv_finished_date, csv_rating, csv_comments):
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"reread: '{csv_reread}'")
    logger.debug(f"csv_status: '{csv_status}'")
    logger.debug(f"csv_finished_date: '{csv_finished_date}'")
    logger.debug(f"csv_rating: {csv_rating}")
    logger.debug(f"csv_comments: '{csv_comments}'")

    reread = None
    if csv_reread != "":
        reread = csv_reread

    status = None
    if csv_status != "":
        status = csv_status

    finished_date = None
    if csv_finished_date != "":
        finished_date = csv_finished_date

    rating_id = None
    if csv_rating != "":
        rating_id = db.rating.select_id_by_stars(csv_rating)

    comments = None
    if csv_comments != "":
        comments = csv_comments

    note_id = db.note.save(book_id, reread, status, finished_date, rating_id, comments)
    return note_id


def save_translators(translators_str):
    """
    Multiple translators are separated by "&".
    No effort is made at this time to break translator names into
    first name, middle name, and last name.
    """
    logger.debug(f"translators_str: '{translators_str}'")
    translators = translators_str.split(sep="&")
    logger.debug(f"translators: {translators}")
    translator_ids = []
    for translator in translators:
        translator = translator.strip()
        if translator != "":
            translator_id = db.translator.save(translator)
            translator_ids.append(translator_id)
    logger.debug(f"translator ids: {translator_ids}")
    return translator_ids

