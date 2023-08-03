# reverse_belts.py
"""
An example of how to use `reverse_belts` on a passed in blueprint or blueprint book.
`reverse_belts` reverses the direction of belt entities in-place such that they 
preserve their continuity, such as around corners. The script prompts the user
for a blueprint string input from stdin.

If a blueprint string is passed in, a blueprint string is output to stdout which
corresponds to every belt entity reversed, including undergrounds and splitters.

If a blueprint book is passed in, the script recurses through all sub-blueprint
books and sub-blueprints and flips the belts inside all of them. Any upgrade/
deconstruction planner inside any of the nested blueprint books are ignored. 
The resultant blueprint book with all belts reversed is printed back to stdout.

If a upgrade/deconstruction planner is passed in, the script prints "Unexpected 
blueprintable type" and exits.
"""

from draftsman.blueprintable import get_blueprintable_from_string, BlueprintBook
from draftsman.extras import reverse_belts


def main() -> None:
    def flip_blueprint_book(bpb: BlueprintBook) -> None:
        for blueprintable in bpb.blueprints:
            if blueprintable.item == "blueprint":
                reverse_belts(blueprintable)
            elif blueprintable.item == "blueprint-book":
                flip_blueprint_book(blueprintable)
            else:
                pass  # Ignore

    bp_string = input()
    blueprintable = get_blueprintable_from_string(bp_string)

    if blueprintable.item == "blueprint":
        reverse_belts(blueprintable)
    elif blueprintable.item == "blueprint-book":
        flip_blueprint_book(blueprintable)
    else:
        print("Unexpected blueprintable type")
        return

    print(blueprintable.to_string())


if __name__ == "__main__":
    main()
