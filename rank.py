import random
import argparse
import shutil
import sys
import json
import io


ENCODING = "utf-8"


class EloItem:
    """Represents an item with an Elo rating for comparison purposes

    Details on the Elo rating system:
    https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details

    Attributes:
        name: Name or identifier for the item
        rating: The item's current Elo rating. Higher means more preferred (default: 1500)

    Methods:
        from_dict(d): [Class Method] Creates an EloItem object from a dictionary representation
        to_json(): Returns a dictionary representation suitable for JSON serialization
        expected_score(other_item): Probability for this item to beat other_item
        update_rating(opponenet, did_win, k): Updates this item's rating based on opponent and match outcome

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

    def __repr__(self):
        return f"{self.name}: {self._rating}"

    def __str__(self):
        return self.name

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
            dict: key-value pairs of the class' attributes
        """
        return {"name": self.name, "rating": self.rating}

    def expected_score(self, other_item: "EloItem"):
        """Calculate the expected score of this item when compared against other_item
        The expected score is a probability ranging from 0 to 1,
        with a score of 1 meaning this item will win the comparison 100% of the time

        Args:
            other_item: The opposing EloItem

        Returns:
            float: a value between 0 and 1, representing win probability
        """
        return 1 / (1 + 10 ** ((other_item.rating - self.rating) / 400))

    def update_rating(self, opponent: "EloItem", did_win: bool, k: int = 40):
        """Updates this item's rating based on opponent and match outcome

        Args:
            opponent: The opposing EloItem
            did_win: Flag indicating if this item won the matchup
            k (optional): The K-factor, determining the magnitude of rating updates (default: 40)
        """
        exp_score = self.expected_score(opponent)

        if did_win:
            rating_change = round(k * (1 - exp_score))
        else:
            rating_change = round(k * (0 - exp_score))

        self.rating += rating_change


def update_elo_ratings(winner: EloItem, loser: EloItem):
    """Updates the Elo ratings for the items after a matchup

    Args:
        winner: EloItem representing the winner
        loser: EloItem representing the loser
    """
    winner.update_rating(loser, True)
    loser.update_rating(winner, False)


def get_matchup(items: list[EloItem]):
    """Return two different items from a collection of items

    In the future: Improve selection algorithm, so instead of being a random choice,
        bias the choice based on some heuristic:
        - Track how many times each item has been chosen, ensure each item receives a similar number of matchups
        - Match similarly rated items against each other
        - Break tied ratings by forcing matchups between them

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


def display_results(sorted_items: list[EloItem], file_name: str):
    """Format the results in a ranked list, print to stdout,
    then prompt user to optionally save the result output to a txt file

    Args:
        sorted_items: A sorted list of items, with "best" item first, "worst" last
        file_name: The base file name of the item set
    """
    with io.StringIO() as str_buffer:
        str_buffer.write("\n---- Ranked Results ----\n")

        prev_rating = None
        for i, item in enumerate(sorted_items, 1):
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


def get_args():
    """Parse and return command line arguments in a structured, documented form

    Returns:
        Namespace: Access the arguments through this object's attributes
    """
    parser = argparse.ArgumentParser(
        description="Rank items based on your preferences in head-to-head matchups."
    )
    subparsers = parser.add_subparsers(dest="command")

    parser_new = subparsers.add_parser(
        "new",
        help=(
            "Start a new ranking from a text file of items. "
            "Data will be stored in a 'rankinfo' file as JSON."
        ),
    )
    parser_new.add_argument(
        "input_filename", help="Plaintext file with one item name per line."
    )

    parser_load = subparsers.add_parser(
        "load",
        help=(
            "Load a saved 'rankinfo' file and resume comparisons "
            "to continue refining an existing item set."
        ),
    )
    parser_load.add_argument(
        "rankinfo_filename", help="JSON file containing saved ranking data."
    )

    return parser.parse_args()


def main():
    """Parses command-line arguments, manages item ranking, and saves results.

    Reads items from a file ('new' command) or loads them from a saved
    ranking ('load' command). Conducts head-to-head comparisons, updates
    item rankings using the Elo system, then displays and saves the final
    results.
    """
    args = get_args()

    if args.command == "new":
        with open(args.input_filename, encoding=ENCODING) as fp_read:
            items = [EloItem(line.strip()) for line in fp_read]
            base_file_name = args.input_filename.split(".")[0]
    elif args.command == "load":
        # Load from existing item set
        with open(args.rankinfo_filename, encoding=ENCODING) as fp_read:
            item_dicts = json.load(fp_read)
            items = [EloItem.from_dict(d) for d in item_dicts]
            base_file_name = args.rankinfo_filename.split("_")[1].split(".")[0]

    while present_matchup_and_update(items):
        pass

    # Mode 'w' will overwrite the file contents if file already exists
    with open(
        f"rankinfo_{base_file_name}.json", mode="w+", encoding=ENCODING
    ) as fp_write:
        # Construct a json array of the items, converting each item to json-dumpable format
        json.dump([item.to_json() for item in items], fp_write, indent=2)

    # Sort by rating, high to low
    items.sort(key=lambda item: item.rating, reverse=True)
    display_results(items, base_file_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
