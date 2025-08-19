# huge_blueprint_book.py

from draftsman.blueprintable import get_blueprintable_from_string


def main():
    with open("test/performance/huge_blueprint_book.txt") as file:
        book = get_blueprintable_from_string(file.read())
    return book


if __name__ == "__main__":
    main()
