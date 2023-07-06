# item_requester.py

"""
Simple command line interface script that modifies all entities in an input
blueprint string to request a certain amount of an item. Would normally be used
to request modules for assembling machines/beacons, but works with any entity
with an inventory which means that you can do interesting things with it.
"""

from draftsman.blueprintable import Blueprint


def main():
    print("Input a blueprint string:")

    blueprint_string = input()
    bp = Blueprint(blueprint_string)

    print("What entity do you want to request items to?")

    entity_name = input()
    matching_entities = bp.find_entities_filtered(name=entity_name)
    assert len(matching_entities) > 0, "No entities with name '{}' in blueprint".format(entity_name)

    print("What item would you like to request for that entity?")
    item_name = input()

    print("How much of that item per entity?")
    item_amount = int(input())

    for entity in matching_entities:
        entity.set_item_request(item_name, item_amount)

    print("Output:\n")
    print(bp.to_string())


if __name__ == "__main__":
    main()