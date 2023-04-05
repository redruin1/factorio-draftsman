# blueprint_operands.py
"""
Illustrates `Blueprint`'s custom operators.
"""

from draftsman.blueprintable import Blueprint
from draftsman.classes.entity_list import EntityList


def main():
    smelter = Blueprint(
        """0eNqlld1uhCAQRt9lrrGpCMj6KpumUXfakCgawGaN4d2LNmmb1E1R7sSM5zCf/CzQdBOORmkH1QKqHbSF6rqAVe+67tZ3bh4RKlAOeyCg634dYYetM6rN3iaj6xbBE1D6hneocv9CALVTTuEXaxvMr3rqGzSh4DGFwDjY8OGgV3OAccqfOIEZqkyEJ+/JHxw9givy/3DFD+4+GrQ2c6bWdhyMyxrs3N4c6TeUBSiBmzJhJlsF21GwJAWPUfATCnmsC5GkiOqiPK4o2LEuZJIiqotL0u+mMYr8OclRRDnO7lu6v9FymrSA4nIpkhxxubCTB9CjXHjSkozLRSQ5dnIJZ/52Q1S/LhQCH2jsVkBlzsoLLYXgUkjp/SdkrR+U
"""
    )

    smelter_with_weave = Blueprint(
        """0eNqlluFugyAUhd/l/salICD1VZplsZYtJBYN0KVN47sPXdI0W5tevf/EwP3OOXqBK+y7kx2C8wnqK7i29xHq3RWi+/JNN71Ll8FCDS7ZIzDwzXEa2c62Kbi2+DwF37QWRgbOH+wZaj6y18vPQ7AxFik0Pg59SMXedumuiBjfGVifXHL2V9A8uHz403FvQ6Y8l8Jg6GNe2PuJn4spod4UgwvUhc5P4yTwTznxStqDotWtqM5FGRxcyErmGfIBoiQhKgxCLgml5K9CUSsUi1tRiVGsSQiFQVSk3FEuDAmBcrFdgTDLXPANiYGywflyRikX+hAkBs5HSfpxBYohSYwSxVAr91HxeMvgmtQKuFxoHY3LxZB6AeeD1tMoH2Kz8kh48n0FrX9RuQha/+JyoZ3GGxRDkhj8PyPfieZ7VH13a2PwbUOcJwjDZbUVldbKaGPG8QcZtz5U"""
    )

    # EntityList, TileList, and ScheduleList all implement methods that allow
    # you to get set union, intersection, and difference:

    union = Blueprint()
    union.entities = smelter_with_weave.entities | smelter.entities
    # union.entities = smelter_with_weave.entities.union(smelter.entities)
    print(union.to_string())

    intersection = Blueprint()
    intersection.entities = smelter_with_weave.entities & smelter.entities
    # intersection.entities = smelter_with_weave.entities.intersection(smelter.entities)
    print(intersection.to_string())

    diff = Blueprint()
    diff.entities = smelter_with_weave.entities - smelter.entities
    # diff.entities = smelter_with_weave.entities.difference(smelter.entities)
    print(diff.to_string())

    # For value equality, use `==`
    assert smelter_with_weave.entities == union.entities

    # Blueprints can also be checked for equality
    # Note that despite having the same entities, smelter_with_weave and union
    # are not the same blueprint due to version mismatch and possession of `icons`
    assert smelter_with_weave != union


if __name__ == "__main__":
    main()
