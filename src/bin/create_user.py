r"""
Create an application user.

EXAMPLE
    python3 create_user.py \
        --user          username \
        --email         username@example.com \
        --password      "correct horse battery staple" \
        --log_file      ~/logs/create_user.log \
        --log_level     debug \
        --transaction   commit
"""


import argparse
import logging
import os
import sys
import textwrap
import traceback

import argon2
import dotenv
dotenv.load_dotenv()

# Modify sys.path to find the audiobooks package.
sys.path.append(os.environ.get('AUDIOBOOKS_PYTHONPATH'))
import audiobooks

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Create an application user",
        epilog=textwrap.dedent(rf"""
        Example:
          python3 {os.path.basename(__file__)} \
            --username      username \
            --email         username@example.com \
            --password      "correct horse battery staple" \
            --log_file      logs/create_db.log \
            --log_level     debug \
            --transaction   commit""")
    )
    parser.add_argument(
        "--username",
        help="username for data being loaded",
        required=True,
    )
    parser.add_argument(
        "--email",
        help="user's email address",
        required=True,
    )
    parser.add_argument(
        "--password",
        help="user's password",
        required=True,
    )
    parser.add_argument(
        "--transaction",
        choices=["commit", "rollback"],
        help="commit or roll back changes to the database",
        required=True,
    )
    parser.add_argument(
        "--log_file",
        help="output log file",
        required=True,
    )
    parser.add_argument(
        "--log_level",
        choices=["debug", "info", "warning", "error", "critical"],
        help="logging level",
        required=True,
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    audiobooks.utils.init_logging(args.log_file, args.log_level)
    audiobooks.db.connect(db_file=os.environ.get('AUDIOBOOKS_DB'))
    audiobooks.db.begin_transaction()
    exception_occurred = False
    try:
        ph = argon2.PasswordHasher()
        password_hash = ph.hash(args.password)
        user_id = audiobooks.db.user.insert(args.username, args.email, password_hash)
        # Commit or roll back database changes. If the rollback is successful,
        # the size of the database file will be 0 bytes.
        if args.transaction == "commit":
            print(f"Requested transaction is {args.transaction}: Committing changes...")
            audiobooks.db.commit()
            print("  Done.")
        else:
            print(f"Requested transaction is {args.transaction}: Rolling back changes...")
            audiobooks.db.rollback()
            print("  Done.")
    except Exception as exc:
        # Roll back changes if any exception occurred.
        print("Caught an exception. Rolling back changes...")
        audiobooks.db.rollback()
        print("  Done.")
        print(f"The exception was '{exc}'.")
        traceback.print_exc(file=sys.stdout)
        exception_occurred = True
    finally:
        audiobooks.db.close()

    if exception_occurred:
        sys.exit(1)


if __name__ == "__main__":
    main()
