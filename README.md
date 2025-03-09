# audiobooks

## Introduction

This is a simple Python CGI application for tracking the audiobooks I've read.
I am constrained to use CGI because my shared hosting server supports only PHP
or CGI and not WSGI.

This is a work in progress.

## Configuration

The code is written for Python 3.10.x because that is the version available
on my shared hosting server.

Set up a virtual environment using either venv or virtualenv and install the
python-dotenv package.

Put the location of the SQLite database into a `.env` file in the application's
root directory. For example:

```config
SQLITE3_DB=data/audiobooks.sqlite3
```

## Installation

To be documented.

## Using

The view.cgi script outputs an HTML table containing the information about the
audiobooks I've read, including the title, author, length, publication date,
translator, and narrator.
