
from draftsman.entity import new_entity
from draftsman.data import entities
import pyperclip
import json

def main():
    #print(json.dumps(entities.raw["constant-combinator"], indent=2))
    # print(entities.raw["medium-electric-pole"])
    # for k in entities.raw["medium-electric-pole"]:
    #     print(k)
    entity = new_entity("offshore-pump")

    print(entity.collision_box)
    print(entity.tile_width)
    print(entity.tile_height)

    print(entities.storage_tanks)

if __name__ == "__main__":
    main()