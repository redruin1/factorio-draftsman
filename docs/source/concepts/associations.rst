Associations
============

In normal Factorio blueprint strings, associations between entities are usually indicated by an integer, which is the index of the entity in the master blueprint's ``entities`` list.
Consider this hypothetical example, where we specify a circuit connection between two inserters:

.. code-block:: python

    blueprint = Blueprint()

    blueprint.entities.append("inserter", tile_position = [-1, 0]) # entity[0]
    blueprint.entities.append("inserter", tile_position = [+1, 0]) # entity[1]

    # Add a red wire connection between entity number 0 and entity number 1
    blueprint.add_circuit_connection("red", 0, 1)
    
However, ``blueprint.entities`` at this point is by no means static, and the indices of each entity is subject to change at any point. 
If one of the connected entities is deleted, the connection would fail without warning because the opposite side would have no knowledge that its pair has been removed.
Even worse, if there were other entities in the blueprint when the entity was removed, and another entity occipies the index that the deleted entity used to exist in, the connection might attempt to join to an entirely different entity!

.. code-block:: python

    # Continuing on from above:
    # If we insert a new entity inbetween the two inserters
    blueprint.entities.insert(1, "wooden-chest", tile_position = (0, 0))

    # After translating into 0-indexed space, we now have:
    # [0]: "inserter": connected to entities[1]
    # [1]: "wooden-chest": No connections
    # [2]: "inserter": connected to entities[0]

    # This breaks at least one connection, and both would have broken if we inserted
    # the wooden-chest at the beginning instead of the middle.
    
    
Clearly, static integers are not enough to keep track of an entity's associations with each other.
The solution that Draftsman uses is ``Associations``, which are loose wrappers around ``weakref.ref`` that point to other ``Entity`` objects.
By using direct references, we alleviate the problem of constantly changing connections every time the parent order changes, as the reference points to the memory location of the data itself instead of a seperate marker:

.. code-block:: python

    # What you would actually see in Draftsman:
    blueprint = Blueprint()

    blueprint.entities.append("inserter", tile_position = [-1, 0])
    blueprint.entities.append("inserter", tile_position = [+1, 0])
    blueprint.add_circuit_connection("red", 0, 1)
    blueprint.entities.insert(1, "wooden-chest", tile_position = (0, 0))

    print(blueprint.wires)
    # [[<Association to Inserter at 0x...>, 1, <Association to Inserter at 0x...>, 1]]

Using references also keeps associated entities perfectly up to date with their connections, as they point to the same data:

.. code-block:: python

    from draftsman.classes.association import Association

    blueprint = Blueprint()

    blueprint.entities.append("inserter", tile_position = [-1, 0])
    blueprint.entities.append("inserter", tile_position = [+1, 0])

    blueprint.add_circuit_connection("red", 0, 1)

    # Lets change one of the attributes of the first inserter
    blueprint.entities[0].id = "test"
    
    # Now lets check the association of the second inserter
    association = blueprint.wires[0][2]
    assert isinstance(association, Association)

    # Associations behave just like weakref.ref, calling it points to the original object
    assert isinstance(assocition(), Inserter)
    
    # We can query the ID of the entity, and we find it's up to date
    print(association().id) # "test"

By using ``weakrefs`` instead of direct references, a connection cannot keep an Entity from being deleted even when it still has other entities that associate with it.
This prevents connections that should no longer be valid from being made by connecting to entities that are kept "alive" by the connection itself.
This also has the benefit of keeping memory usage as small as possible.
Associations default to ``None`` when the entity it should point to was collected, which rightfully throws an error when attempting to export:

.. code-block:: python

    blueprint = Blueprint()

    blueprint.entities.append("inserter", tile_position = [-1, 0])
    blueprint.entities.append("inserter", tile_position = [+1, 0])
    blueprint.add_circuit_connection("red", 0, 1)

    del blueprint.entities[1]

    print(blueprint.wires[0])
    # [<Association to Inserter at 0x0000022E411B7ED0>, 1, <Association to None>, 1]

    print(blueprint.to_string())
    # InvalidAssociationError: Association points to entity None which does not exist in this blueprint

When exporting to Factorio, Associations are converted to their numeric index in the exported object to comply with the blueprint string format.
This process also works the other way; connections in imported blueprint strings are automatically converted to Associations on import:

.. code-block:: python

    # Basically identical to the blueprint above, two inserters connected with a red wire
    blueprint.load_from_string("0eNqdkN0KgzAMhd8l150s1bKtrzJk+BNGQaO0dUyk7762uxG8GbsJOeXkfGk2aIeFZmvYg97AdBM70PcNnHlyM6Q3v84EGoynEQRwM2bFjqwnC0HEvqc3aAy1AGJvvKFvRhbrg5exjU6Nx2kB8+TiwMSJFENKxEIJWEGfEKtCxfi4ElOXPC6ZMBVL/Z5gopKhDiGIA1X+RC3/pGKmxo/n8+jdNQW8yLrMkFesLjd5URWW6qxC+ABGinpP")

    print(blueprint.entities[0])
    # <Inserter>{'name': 'inserter', 'position': {'x': 311.5, 'y': -114.5}, 'connections': {'1': {'red': [{'entity_id': <Association to Inserter>}]}}}
    print(blueprint.entities[1])
    # <Inserter>{'name': 'inserter', 'position': {'x': 313.5, 'y': -114.5}, 'connections': {'1': {'red': [{'entity_id': <Association to Inserter>}]}}}