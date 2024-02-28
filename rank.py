""" 

"""

import random
import argparse
import shutil
import sys
import json
import io

ENCODING = "utf-8"


class EloItem:
    """Represents an item with an Elo rating for comparison purposes

    Attributes:
        name: Name or identifier for the item
        rating: The item's current Elo rating (default: 1500)

    Methods:
        from_dict(d): [Class Method] Creates an EloItem object from a dictionary representation
        to_json(): Returns a dictionary representation suitable for JSON serialization

    """

    def __init__(self, name: str, rating: int = 1500):
        self.name: str = name
        self._rating: int = rating

    @property
    def rating(self):
        """Current ELO rating of the EloItem"""
        return self._rating

    @rating.setter
    def rating(self, new_rating: int):
        self._rating = new_rating

    @classmethod
    def from_dict(cls, dict_item: dict):
        """Creates an EloItem object from a dictionary

        Args:
            dict_item: A dictionary with 'name' and 'rating' keys

        Returns:
            EloItem: A new EloItem object populated from the dictionary
        """
        new_item = cls(dict_item["name"])
        new_item.rating = dict_item["rating"]
        return new_item

    def to_json(self):
        """Convert class data to json-dumpable format

        Returns:
            Dict: key-value pairs of the class' attributes
        """
        return {"name": self.name, "rating": self.rating}

    def __repr__(self):
        return f"{self.name}: {self._rating}"

    def __str__(self):
        return self.name


def expected_score(rating_a, rating_b):
    """Calculate the expected score of a "player" with rating of rating_a,
    playing against an opponent with rating of rating_b.
    The expected score is a probability ranging from 0 to 1,
    with a score of 1 meaning the "player" will win 100% of the time

    Args:
        rating_a: The "player's" Elo rating
        rating_b: The opponent's Elo rating

    Returns:
        float: a value between 0 and 1
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_elo_ratings(winner: EloItem, loser: EloItem, k: int = 32):
    """Updates the Elo ratings for the items after a matchup

    Args:
        winner: EloItem representing the winner
        loser: EloItem representing the loser
        k (optional): The K-factor, determining the magnitude of rating updates (default: 32)
    """
    expected_a = expected_score(winner.rating, loser.rating)
    expected_b = expected_score(loser.rating, winner.rating)

    winner.rating += round(k * (1 - expected_a))
    loser.rating += round(k * (0 - expected_b))


def display_results(items, file_name):
    """Format the results in a ranked list, print to stdout,
    then prompt user to optionally save the result output to a txt file
    """
    with io.StringIO() as str_buffer:
        str_buffer.write("\n---- Ranked Results ----\n")

        prev_rating = None
        for i, item in enumerate(items, 1):
            if prev_rating == item.rating:
                rank = prev_rank
            else:
                rank = i

            str_buffer.write(f"{(rank):3}) {item} ({item.rating})\n")

            prev_rating = item.rating
            prev_rank = rank

        print(str_buffer.getvalue())

        save_to_file = input("Save results to file? (y/n) ")
        if save_to_file.lower() == "y":
            output_file = write_buffer_to_results(file_name, str_buffer)
            print(f"Results saved to {output_file}")


def get_matchup(items: list[EloItem]):
    """Return two different items from a collection of items

    TODO: Improve selection algorithm, instead of being a random choice,
        bias the choice based on some heuristic:
        - Track how many times each item has been chosen, ensure each item receives a similar number of matchups
        - Match similarly rated items against each other

    Args:
        items: collection of comparable items

    Returns:
        List: Two different items from the input collection
    """
    return random.sample(items, 2)


def present_matchup_and_update(items: list[EloItem]):
    """Presents a matchup, gets user choice, and updates Elo ratings

    Args:
        items: A list of EloItem objects.

    Returns:
        bool: True if the user wants to continue, False to see results
    """
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
        return False

    update_elo_ratings(winner, loser)
    return True


def write_buffer_to_results(file_name: str, str_buffer: io.StringIO):
    """Write the str_buffer to a results file

    Returns:
        str: Filename of the file the results were saved to
    """
    full_file_name = f"results_{file_name}.txt"
    with open(full_file_name, mode="w", encoding=ENCODING) as fp_write:
        # Better than write(str_buffer.getvalue()):
        # https://stackoverflow.com/questions/3253258/what-is-the-best-way-to-write-the-contents-of-a-stringio-to-a-file
        str_buffer.seek(0)
        shutil.copyfileobj(str_buffer, fp_write)
    return full_file_name


def get_args():
    """Parse and return command line arguments in a structured, documented form

    Returns:
        Namespace: Access the arguments through this object's attributes
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
    parser_new.add_argument(
        "input_filename", help="Text file containing items for ranking"
    )

    parser_load = subparsers.add_parser(
        "load",
        help=(
            "Load a saved 'rankinfo' file and resume comparisons "
            "to continue refining an existing item set"
        ),
    )
    parser_load.add_argument("rankinfo_filename", help="rankinfo JSON file to load")

    return parser.parse_args()


def main():
    args = get_args()

    if args.command == "new":
        with open(args.input_filename, encoding=ENCODING) as fp_read:
            items = [EloItem(line.strip()) for line in fp_read]
            file_name = args.input_filename.split(".")[0]
    elif args.command == "load":
        # Load from existing item set
        with open(args.input_filename, encoding=ENCODING) as fp_read:
            item_dicts = json.load(fp_read)
            items = [EloItem.from_dict(d) for d in item_dicts]
            file_name = args.input_filename.split("_")[1].split(".")[0]

    while present_matchup_and_update(items):
        pass

    # Mode 'w' will overwrite the file contents if file already exists
    with open(f"rankinfo_{file_name}.json", mode="w+", encoding=ENCODING) as fp_write:
        json.dump([item.to_json() for item in items], fp_write, indent=2)

    # Sort by rating, high to low
    items.sort(key=lambda item: item.rating, reverse=True)
    display_results(items, file_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
