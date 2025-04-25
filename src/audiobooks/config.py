import os

def get_index_path():
    """
    Return the webserver's path to the index.cgi script, using the
    AUDIOBOOKS_WEBDIR environment variable.
    """
    index_path = f"{os.environ.get('AUDIOBOOKS_WEBDIR')}index.cgi"
    return index_path


def get_js_dir_path():
    """
    Return the webserver's path to the js directory, using the
    AUDIOBOOKS_WEBDIR environment variable.
    """
    js_dir_path = f"{os.environ.get('AUDIOBOOKS_WEBDIR')}js/"
    return js_dir_path


def get_styles_path():
    """
    Return the webserver's path to the styles.css file, using the
    AUDIOBOOKS_WEBDIR environment variable.
    """
    styles_path = f"{os.environ.get('AUDIOBOOKS_WEBDIR')}/css/styles.css"
    return styles_path
