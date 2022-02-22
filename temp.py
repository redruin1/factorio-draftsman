
import draftsman
from draftsman.entity import *
from draftsman.signatures import POSITION_SCHEMA
import pyperclip

def main():
    blueprint = draftsman.Blueprint()

    #print(blueprint.entities)
    #print(blueprint.entity_numbers)
    print(blueprint)
    print(blueprint.to_string())

    test_pos = "wrong as fuck"
    print(POSITION_SCHEMA)
    test_pos = POSITION_SCHEMA.validate(test_pos)
    print(test_pos)


if __name__ == "__main__":
    main()