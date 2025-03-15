"""
Database interactions with tbl_vendor.
"""

import logging

logger = logging.getLogger(__name__)


def create_table(conn):
    logger.debug("Creating tbl_vendor...")
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS
        tbl_vendor
        (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """
    conn.execute(sql_create_table)
    vendors = ["audible.com", "cloudLibrary"]
    for vendor in vendors:
        save(conn, vendor)


def insert(conn, vendor):
    logger.debug(f"vendor: '{vendor}'")
    sql_insert = """
        INSERT INTO tbl_vendor
        (
            name
        )
        VALUES (?)
    """
    cur = conn.execute(sql_insert, (vendor,))
    vendor_id = cur.lastrowid
    logger.debug(f"New vendor_id: {vendor_id}")
    return vendor_id


def save(conn, vendor):
    """
    If the vendor exists, select the existing vendor_id.
    Otherwise, insert the vendor and get the new vendor_id.
    Return the vendor_id.
    """
    logger.debug(f"vendor: '{vendor}'")
    vendor_id = select_id(conn, vendor)
    if vendor_id is None:
        vendor_id = insert(conn, vendor)
    logger.debug(f"vendor_id for vendor '{vendor}': {vendor_id}")
    return vendor_id


def select_id(conn, vendor):
    logger.debug(f"vendor: '{vendor}'")
    sql_select_id = """
        SELECT
            tbl_vendor.id
        FROM
            tbl_vendor
        WHERE
            tbl_vendor.name = ?
    """
    cur = conn.execute(sql_select_id, (vendor,))
    db_row = cur.fetchone()
    logger.debug(f"Returned row for vendor '{vendor}': {db_row}")
    vendor_id = None
    if db_row is not None:
        vendor_id = db_row[0]
    logger.debug(f"Existing vendor_id: {vendor_id}")
    return vendor_id
