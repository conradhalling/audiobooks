"""
CSV file processing code for the audible.com data.
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


def save_data(username, csv_file):
    """
    Given the CSV data file for the given vendor, parse the data fields
    and load the data into the database.
    """
    user_id = db.user.select_user_id(username)
    if user_id is None:
        raise ValueError(f"Invalid username {username}")
    
    vendor = "audible.com"
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
                csv_book_pub_date,
                csv_audio_pub_date,
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
                csv_comments,
            ) = csv_row

            # Process authors.
            logger.debug(f"csv_authors: '{csv_authors}'")
            csv_author_strings = csv_authors.split(" & ")
            logger.debug(f"csv_author_strings: '{csv_author_strings}'")
            author_ids = save_authors(csv_author_strings)

            # Process translators.
            logger.debug(f"csv_translators: '{csv_translators}'")
            if csv_translators == "":
                translator_ids = []
            else:
                csv_translator_strings = csv_translators.split(" & ")
                logger.debug(f"csv_translator_strings: '{csv_translator_strings}'")
                translator_ids = save_translators(csv_translator_strings)

            # Process narrators.
            logger.debug(f"csv_narrators: '{csv_narrators}'")
            if csv_narrators == "":
                narrator_ids = []
            else:
                csv_narrator_strings = csv_narrators.split(" & ")
                logger.debug(f"csv_narrator_strings: '{csv_narrator_strings}'")
                narrator_ids = save_narrators(csv_narrator_strings)

            logger.debug(f"csv_title: '{csv_title}'")
            logger.debug(f"csv_pub_date: '{csv_book_pub_date}'")
            logger.debug(f"csv_audio_pub_date: {csv_audio_pub_date}'")
            logger.debug(f"hours: {csv_hours}")
            logger.debug(f"minutes: {csv_minutes}")
            book_id = save_book(
                csv_title, 
                csv_book_pub_date, 
                csv_audio_pub_date, 
                csv_hours, 
                csv_minutes
            )

            for author_id in author_ids:
                db.book_author.save(book_id, author_id)
            
            for translator_id in translator_ids:
                db.book_translator.save(book_id, translator_id)
            
            for narrator_id in narrator_ids:
                db.book_narrator.save(book_id, narrator_id)
            
            acquisiton_id = save_acquisition(
                user_id,
                book_id, 
                vendor_id,
                csv_acquisition_type, 
                csv_acquisition_date, 
                csv_discontinued,
                csv_audible_credits, 
                csv_price
            )
            
            note_id = save_note(
                user_id,
                book_id,
                csv_status,
                csv_finished_date,
                csv_rating,
                csv_comments
            )


def save_acquisition(
        user_id,
        book_id,
        vendor_id,
        csv_acquisition_type,
        csv_acquisition_date,
        csv_discontinued,
        csv_audible_credits,
        csv_price):
    """
    Convert book acquisition attributes and save the book acquisition.
    """
    csv_acquisition_type = csv_acquisition_type.strip()
    acquisition_types = {
        "Credit": "vendor credit",
        "Extra": "charge",
        "Free": "no charge",
        "Plus": "member benefit",
        "Podcast": "podcast"
    }
    if csv_acquisition_type in acquisition_types:
        acquisition_type = acquisition_types[csv_acquisition_type]
    else:
        raise ValueError(f"csv_acquisition_type '{csv_acquisition_type}' not handled")
    acquisition_type_id = db.acquisition_type.save(acquisition_type)

    if csv_acquisition_date == "":
        raise ValueError("csv_acquistion_date must not be empty")
    
    discontinued = None
    if csv_discontinued != "":
        discontinued = csv_discontinued
    
    audible_credits = None
    if csv_audible_credits != "":
        audible_credits = csv_audible_credits
    
    price = convert_price(csv_price)

    db.acquisition.save(
        user_id, book_id, vendor_id, acquisition_type_id, csv_acquisition_date,
        discontinued, audible_credits, price)


def save_authors(author_strings):
    """
    author_strings is a list of authors formatted as "surname, forename",
    where multiple words may appear in each of surname and forename. If the
    author has a single name (e.g., "Homer", "Aeschylus", "Colette"), the
    surname is saved as NULL in the database.
    """
    author_ids = []
    for author_string in author_strings:
        logger.debug(f"author_string: '{author_string}'")
        names = author_string.split(",")
        if len(names) == 1:
            surname = ""
            forename = names[0]
        elif len(names) == 2:
            surname = names[0]
            forename = names[1]
        else:
            raise ValueError("Author name '{name_string}' formatted incorrectly with too many commas.")
        surname = surname.strip()
        if surname == "":
            surname = None
        forename = forename.strip()
        if forename == "":
            raise ValueError(f"The author's forename '{forename}' must not be empty.")
        logger.debug(f"surname: '{surname}'")
        logger.debug(f"forename: {forename}'")
        author_id = db.author.save(surname, forename)
        logger.debug(f"author ID: {author_id}")
        author_ids.append(author_id)
    return author_ids


def save_narrators(narrator_strings):
    """
    narrator_strings is a list of narrators formatted as "surname, forename",
    where multiple words may appear in each of surname and forename. If the
    narrator has a single name, the surname is saved as NULL in the database.
    """
    narrator_ids = []
    for narrator_string in narrator_strings:
        logger.debug(f"narrator_string: '{narrator_string}'")
        names = narrator_string.split(",")
        if len(names) == 1:
            forename = names[0]
            surname = None
        elif len(names) == 2:
            surname = names[0]
            forename = names[1]
        else:
            raise ValueError("Narrator name '{name_string}' formatted incorrectly with too many commas.")
        if surname is not None:
            surname = surname.strip()
            if surname == "":
                surname = None
        forename = forename.strip()
        if forename == "":
            raise ValueError(f"The narrator's forename '{forename}' must not be empty.")
        logger.debug(f"surname: '{surname}'")
        logger.debug(f"forename: {forename}'")
        narrator_id = db.narrator.save(surname, forename)
        logger.debug(f"narrator ID: {narrator_id}")
        narrator_ids.append(narrator_id)
    return narrator_ids


def save_translators(translator_strings):
    """
    translatorstrings is a list of translators formatted as "surname, forename",
    where multiple words may appear in each of surname and forename. If the
    translator has a single name, the surname is saved as NULL in the database.
    """
    logger.debug(f"translator_strings: '{translator_strings}'")
    translator_ids = []
    for translator_string in translator_strings:
        logger.debug(f"translator_string: '{translator_string}'")
        names = translator_string.split(",")
        if len(names) == 1:
            forename = names[0]
        elif len(names) == 2:
            surname = names[0]
            forename = names[1]
        else:
            raise ValueError("Translator name '{name_string}' formatted incorrectly with too many commas.")
        surname = surname.strip()
        if surname == "":
            surname = None
        forename = forename.strip()
        if forename == "":
            raise ValueError(f"The translator's forename '{forename}' must not be empty.")
        logger.debug(f"surname: '{surname}'")
        logger.debug(f"forename: {forename}'")
        translator_id = db.translator.save(surname, forename)
        logger.debug(f"translator ID: {translator_id}")
        translator_ids.append(translator_id)
    return translator_ids


def save_book(title, book_pub_date, audio_pub_date, hours, minutes):
    logger.debug(f"title: '{title}'")
    logger.debug(f"book_pub_date: '{book_pub_date}'")
    logger.debug(f"audio_pub_date: '{audio_pub_date}'")
    logger.debug(f"hours: {hours}")
    logger.debug(f"minutes: {minutes}")
    if book_pub_date == "":
        book_pub_date = None
    if audio_pub_date == "":
        audio_pub_date = None
    book_id = db.book.save(title, book_pub_date, audio_pub_date, hours, minutes)
    logger.debug(f"book_id: {book_id}")
    return book_id


def save_note(user_id, book_id, csv_status, csv_finished_date,
            csv_rating, csv_comments):
    logger.debug(f"user_id: {user_id}")
    logger.debug(f"book_id: {book_id}")
    logger.debug(f"csv_status: '{csv_status}'")
    logger.debug(f"csv_finished_date: '{csv_finished_date}'")
    logger.debug(f"csv_rating: {csv_rating}")
    logger.debug(f"csv_comments: '{csv_comments}'")

    status_id = None
    if csv_status != "":
        status_id = db.status.save(csv_status)

    finished_date = None
    if csv_finished_date != "":
        finished_date = csv_finished_date

    rating_id = None
    if csv_rating != "":
        rating_id = db.rating.select_id_by_stars(csv_rating)

    comments = None
    if csv_comments != "":
        comments = csv_comments

    note_id = db.note.save(user_id, book_id, status_id, finished_date,
                        rating_id, comments)
    return note_id
