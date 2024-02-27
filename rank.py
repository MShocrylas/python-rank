import random
import argparse
import sys
import json


ENCODING = "utf-8"


class EloItem:
    """Represents an item with an Elo rating for comparison purposes

    Attributes:
        name (str): Name or identifier for the item
        rating (int): The item's current Elo rating (default: 1500)

    Methods:
        from_dict(d): [Class Method] Creates an EloItem object from a dictionary representation
        to_json(): Returns a dictionary representation suitable for JSON serialization

    """

    def __init__(self, name, rating=1500):
        self.name: str = name
        self._rating: int = rating

    def __repr__(self):
        return f"{self.name}: {self._rating}"

    def __str__(self):
        return self.name

    @classmethod
    def from_dict(cls, d):
        """Creates an EloItem object from a dictionary

        Args:
            d (Dict): A dictionary with 'name' and 'rating' keys

        Returns:
            EloItem: A new EloItem object populated from the dictionary
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
        """Current ELO rating of the EloItem"""
        return self._rating

    @rating.setter
    def rating(self, new_rating):
        self._rating = new_rating


def expected_score(rating_a, rating_b):
    """Calculate the expected score of a "player" with rating of rating_a,
    playing against an opponent with rating of rating_b

    Args:
        rating_a (int)
        rating_b (int)

    Returns:
        float: a value between 0 and 1
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_elo_ratings(winner, loser, k=32):
    """Updates the Elo ratings for the items after a matchup

    Args:
        winner (EloItem): EloItem representing the winner
        loser (EloItem): EloItem representing the loser
        k (int, optional): The K-factor, determining the magnitude of updates. Defaults to 32.
    """
    expected_a = expected_score(winner.rating, loser.rating)
    expected_b = expected_score(loser.rating, winner.rating)

    winner.rating += round(k * (1 - expected_a))
    loser.rating += round(k * (0 - expected_b))


def get_matchup(items):
    """Return two different items from a collection of items

    TODO: Improve selection algorithm, instead of being a random choice,
        bias the choice based on some heuristic:
        - Track how many times each item has been chosen, ensure each item receives a similar number of matchups
        - Match similarly rated items against each other

    Args:
        items (List): collection of comparable items

    Returns:
        List: Two different items from the input collection
    """
    return random.sample(items, 2)


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
    parser_new.add_argument("txt_filename")

    parser_load = subparsers.add_parser("load", help="TEMP")
    parser_load.add_argument("json_filename")

    return parser.parse_args()


def main():
    args = get_args()

    if args.command == "new":
        with open(args.txt_filename, encoding=ENCODING) as fp_read:
            items = [EloItem(line.strip()) for line in fp_read]
            file_name = args.txt_filename.split(".")[0]
    elif args.command == "load":
        # Load from existing item set
        with open(args.json_filename, encoding=ENCODING) as fp_read:
            item_dicts = json.load(fp_read)
            items = [EloItem.from_dict(d) for d in item_dicts]
            file_name = args.json_filename.split("_")[1].split(".")[0]

    # Choose matchups randomly, but each item should be selected once before repeats

    while True:
        item_1, item_2 = get_matchup(items)

        print(f"\nWhich do you prefer:\n" f" [1] {item_1}\n" f" [2] {item_2}\n")
        choice = input("Choose 1 or 2 (other to see results): ")

        if choice == "1":
            winner = item_1
            loser = item_2
        elif choice == "2":
            winner = item_2
            loser = item_1
        else:
            break

        update_elo_ratings(winner, loser)

    print(items)
    # Overwrite if already exists
    with open(f"rankinfo_{file_name}.json", mode="w+", encoding=ENCODING) as fp_write:
        json.dump([item.to_json() for item in items], fp_write, indent=2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
