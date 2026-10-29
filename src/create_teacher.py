from getpass import getpass

from auth import add_teacher


def main() -> None:
    username = input("Teacher username: ")
    password = getpass("Teacher password (12+ characters): ")
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    try:
        add_teacher(username, password)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print("Teacher account created.")


if __name__ == "__main__":
    main()