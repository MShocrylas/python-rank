import random
import argparse
import sys
import json


ENCODING = "utf-8"


class ELOItem:
    """_summary_"""

    def __init__(self, name):
        self.name = name
        self._rating = 0

    def __repr__(self):
        return f"{self.name}: {self._rating}"

    def to_json(self):
        """Convert class data to json-dumpable format

        Returns:
            dict: key-value pairs of the class' attributes
        """
        return {"name": self.name, "rating": self.rating}

    @property
    def rating(self):
        """Current ELO rating of the Item"""
        return self._rating

    @rating.setter
    def rating(self, new_rating):
        self._rating = new_rating


def get_args():
    """Parse and return command line arguments in a structured, documented form

    Returns:
        ArgumentParser: Access the arguments through this class' attributes
    """
    parser = argparse.ArgumentParser(
        description="Rank a set of items based on 1 on 1 preference"
    )
    subparsers = parser.add_subparsers(dest="command")

    parser_new = subparsers.add_parser("new", help="TEMP")
    parser_new.add_argument("text_filename")

    parser_load = subparsers.add_parser("load", help="TEMP")
    parser_load.add_argument("items_filename")

    return parser.parse_args()


def get_matchup(items):
    return random.sample(items, 2)


def main():
    args = get_args()

    if args.command == "new":
        with open(args.text_filename, encoding=ENCODING) as fp_read:
            items = [ELOItem(line.strip()) for line in fp_read]

        file_name = args.text_filename.split(".")[0]
        with open(
            f"rankinfo_{file_name}.json", mode="w+", encoding=ENCODING
        ) as fp_write:
            json.dump([item.to_json() for item in items], fp_write, indent=2)

    elif args.command == "load":
        # Load from existing item set
        pass

    # Choose matchups randomly, but each item should be selected once before repeats

    while True:
        item_1, item_2 = get_matchup(items)
        print(f"\nWhich do you prefer:\n" f" [1] {item_1}\n" f" [2] {item_2}\n")
        choice = input()
        if choice == "1":
            item_1.rating = 1500
        elif choice == "2":
            item_2.rating = 1500
        else:
            break

    print(items)

    return 0


if __name__ == "__main__":
    sys.exit(main())
