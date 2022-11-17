# Must have a local datastore instance started.

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import argparse
from common.datastore import db
from dkc.auth.register import create_user_application


parser = argparse.ArgumentParser()
parser.add_argument(
    "number_of_users",
    type=int,
    default=100,
    help="Number of users to seed the database with",
)
parser.add_argument(
    "--starting_number",
    type=int,
    metavar="N",
    default=1,
    help="User number to start with",
)

if __name__ == "__main__":
    args = parser.parse_args()
    with db.context():
        start = args.starting_number
        end = start + args.number_of_users
        for i in range(start, end):
            user = create_user_application(
                f"email{i}@{i}.com", "password", f"First{i}", f"Last{i}"
            )
            print(user)
