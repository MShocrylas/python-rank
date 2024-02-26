import random
import argparse
import sys


class Item:
    def __init__(self, name):
        self.name = name
        self.rating = 0

    def __repr__(self):
        return self.name


def main():
    parser = argparse.ArgumentParser(
        description="Rank a set of items based on 1 on 1 preference"
    )
    parser.add_argument("items_filename")
    args = parser.parse_args()

    with open(args.items_filename) as fp:
        items = [Item(line.strip()) for line in fp]
    print(items)

    # Choose matchups randomly, but each item should be selected once before repeats

    while True:
        item_1, item_2 = random.sample(items, 2)
        print(f"\nWhich do you prefer:\n" f" [1] {item_1}\n" f" [2] {item_2}\n")
        choice = input()
        if choice == "1":
            pass
        elif choice == "2":
            pass
        else:
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
