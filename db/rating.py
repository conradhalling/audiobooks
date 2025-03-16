"""
Database interactions with tbl_rating.
"""

import logging
logger = logging.getLogger(__name__)

from . import conn


def create_table():
    """
    Create tbl_rating.
    """
    logger.debug("Creating table tbl_rating...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_rating
        (
            id INTEGER PRIMARY KEY,
            stars INTEGER NOT NULL UNIQUE,
            description TEXT NOT NULL UNIQUE
        )
    """
    conn.conn.execute(sql_create_table)
    ratings = [
        (0, "terrible",),
        (1, "poor",),
        (2, "fair",),
        (3, "good",),
        (4, "very good",),
        (5, "excellent",),
    ]
    for rating in ratings:
        save(stars=rating[0], description=rating[1])


def insert(stars, description):
    """
    Insert the rating and return the new rating_id.
    Raises an exception if the rating is already in the database.
    """
    logger.debug(f"stars: {stars}")
    logger.debug(f"description: '{description}'")
    sql_insert = """
        INSERT INTO tbl_rating
        (
            stars,
            description
        )
        VALUES (?, ?)
    """
    cur = conn.conn.execute(sql_insert, (stars, description,))
    rating_id = cur.lastrowid
    logger.debug(f"New rating_id for stars {stars} description '{description}': {rating_id}")
    return rating_id


def save(stars, description):
    logger.debug(f"stars: {stars}")
    logger.debug(f"description: {description}")
    logger.debug(f"rating: ({stars}, '{description}'")
    rating_id = select_id(stars, description)
    if rating_id is None:
        rating_id = insert(stars, description)
    logger.debug(f"rating_id for stars {stars} description '{description}': {rating_id}")
    return rating_id


def select_id(stars, description):
    """
    Select and return the ID for the rating.
    Return None if the rating is not in the database.
    """
    logger.debug(f"stars: {stars}")
    logger.debug(f"description: {description}")
    sql_select_id = """
        SELECT
            tbl_rating.id
        FROM
            tbl_rating
        WHERE
            tbl_rating.stars = ?
            and tbl_rating.description = ?
    """
    cur = conn.conn.execute(sql_select_id, (stars, description,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for stars {stars} and description '{description}': {db_row}")
    rating_id = None
    if db_row is not None:
        rating_id = db_row[0]
    return rating_id


def select_id_by_stars(stars):
    """
    Select and return the ID for the rating.
    Return None if the rating is not in the database.
    """
    logger.debug(f"stars: {stars}")
    sql_select_id = """
        SELECT
            tbl_rating.id
        FROM
            tbl_rating
        WHERE
            tbl_rating.stars = ?
    """
    cur = conn.conn.execute(sql_select_id, (stars,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for stars {stars}': {db_row}")
    rating_id = None
    if db_row is not None:
        rating_id = db_row[0]
    return rating_id
