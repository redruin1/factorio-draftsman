# blueprint_operands.py
"""
Illustrates `EntityList`'s custom set operators.
"""

from draftsman.blueprintable import Blueprint
from draftsman.classes.entity_list import EntityList


def main():
    # A set of 4 furnaces with some belts
    smelter = Blueprint(
        """0eNqlld1uhCAQRt9lrrGpCMj6KpumUXfakCgawGaN4d2LNmmb1E1R7sSM5zCf/CzQdBOORmkH1QKqHbSF6rqAVe+67tZ3bh4RKlAOeyCg634dYYetM6rN3iaj6xbBE1D6hneocv9CALVTTuEXaxvMr3rqGzSh4DGFwDjY8OGgV3OAccqfOIEZqkyEJ+/JHxw9givy/3DFD+4+GrQ2c6bWdhyMyxrs3N4c6TeUBSiBmzJhJlsF21GwJAWPUfATCnmsC5GkiOqiPK4o2LEuZJIiqotL0u+mMYr8OclRRDnO7lu6v9FymrSA4nIpkhxxubCTB9CjXHjSkozLRSQ5dnIJZ/52Q1S/LhQCH2jsVkBlzsoLLYXgUkjp/SdkrR+U"""
    )

    # Same blueprint as above with some additional belts in-between
    smelter_with_weave = Blueprint(
        """0eNqlluFugyAUhd/l/salICD1VZplsZYtJBYN0KVN47sPXdI0W5tevf/EwP3OOXqBK+y7kx2C8wnqK7i29xHq3RWi+/JNN71Ll8FCDS7ZIzDwzXEa2c62Kbi2+DwF37QWRgbOH+wZaj6y18vPQ7AxFik0Pg59SMXedumuiBjfGVifXHL2V9A8uHz403FvQ6Y8l8Jg6GNe2PuJn4spod4UgwvUhc5P4yTwTznxStqDotWtqM5FGRxcyErmGfIBoiQhKgxCLgml5K9CUSsUi1tRiVGsSQiFQVSk3FEuDAmBcrFdgTDLXPANiYGywflyRikX+hAkBs5HSfpxBYohSYwSxVAr91HxeMvgmtQKuFxoHY3LxZB6AeeD1tMoH2Kz8kh48n0FrX9RuQha/+JyoZ3GGxRDkhj8PyPfieZ7VH13a2PwbUOcJwjDZbUVldbKaGPG8QcZtz5U"""
    )

    # EntityList, TileList, and ScheduleList all implement methods that allow
    # you to get the set union, intersection, and difference:

    # The union in this case would be any entity that either in one blueprint OR
    # the other, without duplicates
    # Because the two overlap each other, in this case their union is equivalent
    # to `smelter_with_weave`
    union = Blueprint()
    union.entities = smelter_with_weave.entities | smelter.entities
    # union.entities = smelter_with_weave.entities.union(smelter.entities)
    print("union:\n", union.to_string())

    # The intersection in this case is any entity that exists exactly the same
    # in BOTH blueprints
    # Only the furnaces are shared between the two blueprints, so their
    # intersection is equivalent to `smelter`
    intersection = Blueprint()
    intersection.entities = smelter_with_weave.entities & smelter.entities
    # intersection.entities = smelter_with_weave.entities.intersection(smelter.entities)
    print("intersection:\n", intersection.to_string())

    # The difference is (unsurprisingly) the difference between the two blueprints
    # This blueprint contains just the belt weave itself and no furnaces
    difference = Blueprint()
    difference.entities = smelter_with_weave.entities - smelter.entities
    # diff.entities = smelter_with_weave.entities.difference(smelter.entities)
    print("difference:\n", difference.to_string())

    # For value equality, use `==`
    assert smelter_with_weave.entities == union.entities

    # Blueprints themselves can also be checked for equality
    # Note that despite having the same entities, smelter_with_weave and union
    # are not the same blueprint due to possession of `icons` table and (possibly) version mismatch
    assert smelter_with_weave != union

    # This notation also provides a neat pneumonic for removing certain entities.
    # If we want to simply remove a set of entities, first we get a list of all
    # the entities we want to remove
    belt_entities = smelter_with_weave.find_entities_filtered(
        type={"transport-belt", "splitter", "underground-belt"}
    )
    # Then we can simply "subtract" those entities from the parent blueprint
    no_belts = Blueprint()
    no_belts.entities = smelter_with_weave.entities - belt_entities
    # And the resulting blueprint will simply be the original minus the belts:
    print("no_belts:\n", no_belts.to_string())
    assert (
        len(
            no_belts.find_entities_filtered(
                type={"transport-belt", "splitter", "underground-belt"}
            )
        )
        == 0
    )


if __name__ == "__main__":  # pragma: no coverage
    main()
