"""
Parse the Excel file and load the data into a DataFrame.

Usage:
    python3 parse_xlsx.py  > parse_xlsx.log
"""

import openpyxl
import pandas as pd
import sqlalchemy

import audiobooks


def parse_xlsx(excel_filepath):
    wb = openpyxl.load_workbook(excel_filepath)
    ws = wb.active
    data = ws.values
    cols = next(data)
    data = list(data)
    df = pd.DataFrame(data, columns=cols)
    return df


if __name__ == "__main__":
    # Remove any existing database file.
    sqlite3_filepath = "audiobooks.sqlite3"
    audiobooks.remove_sqlite3_file(sqlite3_filepath)

    # Create the database and its tables.
    audiobooks.init_sqlite()
    url = "sqlite:///" + sqlite3_filepath
    engine = sqlalchemy.create_engine(url, future=True, echo=True)
    audiobooks.create_tables(engine)

    # Read the data from the Excel file into a pandas DataFrame.
    excel_filepath = "/Users/halto/OneDrive/Documents/Audiobooks.xlsx"
    df = parse_xlsx(excel_filepath)
    print(df.info())
    print(df)

    # Insert the data into the database tables.
    audiobooks.insert_data(engine, df)

    # Log status.
    print("Script {} completed successfully.".format(__file__))
