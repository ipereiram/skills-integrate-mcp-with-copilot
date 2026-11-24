"""Generate a salted teacher credential record for teachers.json."""

import getpass
import json
import sys

from auth import create_teacher_record


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        raise SystemExit("Usage: python src/create_teacher.py <username>")

    password = getpass.getpass("Teacher password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if not password or password != confirmation:
        raise SystemExit("Passwords must be non-empty and match")

    print(json.dumps(create_teacher_record(sys.argv[1].strip(), password), indent=2))


if __name__ == "__main__":
    main()
