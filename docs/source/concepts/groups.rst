Groups
======

:py:class:`.Group` classes in Draftsman are one of it's most powerful features.
Groups allow you to create "sub-blueprints" that can be placed inside a blueprint multiple times, or even inside other Group objects.
This allows the user to fragment blueprints into unique, discrete components that can be specified once and then reused multiple times, reducing repetitive code and improving readability on complex blueprints.

Creating Group objects is just as easy as making Blueprint objects:

.. code-block:: python

    from draftsman.blueprintable import Group

    group = Group()

Groups share almost all functionality with :py:class:`Blueprint`, except for blueprint-specific metadata:

.. code-block:: python

    group.entities.append("wooden-chest")
    group.tiles.append(Tile("landfill"), copy=False)

    assert len(group.find_entities_filtered(type="container")) == 1
    assert group.get_dimensions() == (1, 1)

    group.label # AttributeError: 'Group' object has no attribute 'label'
    group.description # AttributeError: 'Group' object has no attribute 'description'
    group.version # AttributeError: 'Group' object has no attribute 'version'

Groups also have their own :py:attr:`~Group.groups` attribute, allowing you to make trees of nested Groups:

.. code-block:: python

    child_group = Group()
    child_group.entities.append("iron-chest", tile_position=(2, 2))
    child_group.tiles.append("concrete", tile_position=(2, 2))
    
    group.groups.append(child_group)
    assert len(group.entities) == 1
    assert len(group.tiles) == 1
    assert len(group.groups) == 1
    assert len(group.groups[0].entities) == 1
    assert len(group.groups[0].tiles) == 1
    assert group.get_dimensions() == (3, 3)

Groups can then simply be added to a parent Blueprint's ``groups`` list, which acts as the root node of the tree:

.. code-block:: python

    blueprint = Blueprint()
    blueprint.groups.append(group)

.. code-block:: text

    0eNp1jtsKwjAMQP8lz1W6santr8iQXSIGuna0nTpK/91tFhGcTyGBc04CNGrEwZL2IAOQxx7k143BHa0jo0GWh1wUQpTHIhOcnxig9uQJHchzeC/TRY99gxZkxkDXPc6uhzEd6l17Q7foBuNmaPEFeILk+5LBtM4Y2Y8m/2jImr+SPEnyRVIx8KTSVwlWte6upNRWn6c+X/sJaI1uLXrcavHUmoEqxheo4WbY

... Which are then automatically "flattened" by Draftsman into an equivalent, 1-dimensional structure when exporting:

.. figure:: ../../img/handbook/groups/groups_example.png

Groups also have a :py:attr:`~Group.position` attribute which allows them to be positioned relative to their parents:

.. code-block:: python

    group = Group()
    group.entities.append("decider-combinator")

    blueprint = Blueprint()
    for i in range(3):
        blueprint.groups.append(group, position=(i * 2, 0))

The final position of the entities/tiles in the resultant blueprint is the total sum of all parent positions plus their own.

Similar to entities, Groups can be given an ID which allows them to be accessed from their ``groups`` list via that name:

.. code-block:: python

    group = Group("some-id")

    blueprint = Blueprint()
    blueprint.groups.append(group, copy=False)
    assert blueprint.groups["some-id"] is group

Two groups at the same "level" cannot share the same ID, as that would lead to ambiguity:

.. code-block:: python

    group = Group("some-id")

    blueprint.groups.append(group) # Okay
    blueprint.groups.append(group) # DuplicateIDError: 'some-id'
    blueprint.groups.append(group, id="some-other-id") # Okay

However, Group children can share the same ID with other entities in different groups, since they are logically separated:

.. code-block:: python

    group = Group()
    group.entities.append("wooden-chest", tile_position=(0, 0), id="A")
    group.entities.append("iron-chest", tile_position=(1, 0), id="B")
    group.entities.append("steel-chest", tile_position=(2, 0), id="C")

    blueprint = Blueprint()
    blueprint.groups.append(group, id="group_1")
    blueprint.groups.append(group, id="group_2", position=(0, 1))
    # ID "A" appears multiple times in `blueprint`, but are accessed differently
    # ("group_1", "A") vs ("group_2", "A")

Many functions used for setting up Associations take a tuple of strings, allowing you to reference nested entities:

.. code-block:: python

    left_group = Group("left", position=(-2, 0))
    left_group.entities.append("medium-electric-pole", id="power")
    
    right_group = Group("right", position=(2, 0))
    right_group.entities.append("medium-electric-pole", id="power")

    blueprint = Blueprint()
    blueprint.groups = [left_group, right_group]
    blueprint.add_power_connection(
        entity_1=("left", "power"),
        entity_2=("right", "power")
    )

.. code-block:: text

    0eNqVjUEOgjAURO8y6w+hhKrtVQwxgn/xE1pIKSppendRNySuXM5L5r2Eblh4CuIjbIJEdrA7RrhzmGX0sPpQm8YYfWyUqaoT4SGBZ9jzWZGmmnTbEthHifLB6TvWi19cxwFWEfzV8eZ3fJPFFTxwH4P0xTQOvKWmcd7O71bCE7ZQpSassFWpc6YfX/2nr97r2pxfbepR3w==

.. figure:: ../../img/handbook/groups/power_example.png

Giving IDs to groups and their children makes setting up complex connections between them much easier, as long as you keep them descriptive and unique:

.. code-block:: python

    group = Group()
    group.entities.append("decider-combinator", id="dc")

    blueprint = Blueprint()
    for i in range(3):
        blueprint.groups.append(group, id=str(i), position=(i * 2, 0))
        if i != 0:
            blueprint.add_circuit_connection(
                "red",
                entity_1=(str(i-1), "dc"),
                side_1="input",
                entity_2=(str(i), "dc"),
                side_2="input",
            )
            blueprint.add_circuit_connection(
                "green",
                entity_1=(str(i-1), "dc"),
                side_1="output",
                entity_2=(str(i), "dc"),
                side_2="output",
            )

.. code-block:: text

    0eNqVjssKgzAQRf9l1lMxMbY1vyKh+JhFoEaJsa2E/HundiMUCu7OvXDPTIT2vtDkrQugI9hAA+hdh/AgP9vRgS7PslJVVV6UqPL8ivC0nmbQdS1QoERhkEkxKSbOWGwdZyZlDAK5YIPdRvEb1ptbhpY8aIHgmoH4ek+d7cmfunForWvC6PmNaZx5+vkjwgt0npUIK6+yPCX8kclDMvlfVhySqb3MpPQGdl1wTA==

.. figure:: ../../img/handbook/groups/connections_example.png

For convenience, you can populate a Group from a compressed blueprint string directly:

.. code-block:: python

    bp_string = """0eNqllGFrwyAQhv/LfdZhkmUl+SujDJNc2wO9FLVjXfC/z2TZBisrLH4S9d7n3pdDJ+jMBc+OOEA7AfUje2ifJ/B0ZG3mM9YWoQXtPdrOEB+l1f2JGGUFUQDxgG/QFnEvADlQIPwkLJvrC19shy4ViLskAefRJ/HIc88EVA+1gOuyxpkdyKzgX4WyWOpkEb87ODwk6iBP+l27QaZQvcOA0uAhJM83CJVNyPewxlC5KVRuCJWdIXsS2YPIn0N5S/iS/u37n6JNnVZ/1RZ/1RZ/d0XpYVJAm+5+/hEBr+j8gqmfyuaxaeqdKutdU8b4AbwVejE="""

    imported_group = Group.from_string(bp_string)
    assert len(imported_group.entities) == 1
    assert len(imported_group.tiles) == 15

Groups import :py:attr:`~.Group.entities`, :py:attr:`~.Group.tiles`, :py:attr:`~.Group.schedules`, :py:attr:`~.Group.wires`, and :py:attr:`~.Group.stock_connections` from the blueprint string (using the ``version`` to determine the imported data format, if present) and all other information is stripped.