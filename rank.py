import random
import argparse
import sys
import json


ENCODING = "utf-8"


class ELOItem:
    """_summary_"""

    def __init__(self, name):
        self.name: str = name
        self._rating: int = 1500  # Default starting rating

    def __repr__(self):
        return f"{self.name}: {self._rating}"

    def __str__(self):
        return self.name

    @classmethod
    def from_dict(cls, d):
        """_summary_

        Args:
            d (Dict): _description_

        Returns:
            _type_: _description_
        """
        new_item = cls(d["name"])
        new_item.rating = d["rating"]
        return new_item

    def to_json(self):
        """Convert class data to json-dumpable format

        Returns:
            Dict: key-value pairs of the class' attributes
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

    parser_new = subparsers.add_parser(
        "new",
        help=(
            "Read a list of items from plain text and generate a rank set "
            "from it stored as JSON in a rankinfo file"
        ),
    )
    parser_new.add_argument("text_filename")

    parser_load = subparsers.add_parser("load", help="TEMP")
    parser_load.add_argument("json_filename")

    return parser.parse_args()


def get_matchup(items):
    return random.sample(items, 2)


def main():
    args = get_args()

    if args.command == "new":
        with open(args.text_filename, encoding=ENCODING) as fp_read:
            items = [ELOItem(line.strip()) for line in fp_read]

    elif args.command == "load":
        # Load from existing item set
        with open(args.json_filename, encoding=ENCODING) as fp_read:
            item_dicts = json.load(fp_read)
            items = [ELOItem.from_dict(d) for d in item_dicts]

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
