Entity IDs
==========

In normal Factorio blueprint strings, associations between entities are usually indicated by ``entity_number``, which is the index of the entity in the internal ``entities`` list.
Consider this hypothetical example, where we specify a circuit connection between two inserters:

.. code-block:: python

    blueprint = Blueprint()

    blueprint.add_entity("inserter", tile_position = [-1, 0]) # entity[0]
    blueprint.add_entity("inserter", tile_position = [+1, 0]) # entity[1]

    # Add a red wire connection between entity number 0 and entity number 1
    blueprint.add_circuit_connection("red", 0, 1)
    
However, ``blueprint.entities`` is by no means static, and the indices of each entity is subject to change at any point. 
If one of the connected entities is deleted, the connection would fail without warning because the opposite side would have no knowledge that its pair has been removed.
Even worse, if there were other entities in the blueprint when the entity was removed, and another entity occipies the index that the deleted entity used to exist in, the connection might attempt to join with an entirely different, unrelated entity!

This manner of association degrades further if you decide that, for convinience, you want to be able to connect entities *outside* of blueprints:

.. code-block:: python

    # I want to connect these two inserters
    inserter1 = Inserter("inserter", tile_position = [-1, 2])
    inserter2 = Inserter("inserter", tile_position = [+1, 2])

    # What entity_number would either of these entities have, when they don't
    # currently exist in any Blueprint?

This is the motivation for using an alternative to ``entity_number`` to set up associations between entities.
The alternative provided by Draftsman is **string IDs**, which solves both of these problems:

.. code-block:: python

    blueprint = Blueprint()

    blueprint.add_entity("inserter", id = "a", tile_position = [-1, 0])
    blueprint.add_entity("inserter", id = "b", tile_position = [+1, 0])

    # These ids are always associated only with the entities that possess them,
    # regardless of their position or orientation within the blueprint's entity
    # list
    blueprint.add_circuit_connection("red", "a", "b")

    inserter1 = Inserter("inserter", id = "c", tile_position = [-1, 2])
    inserter2 = Inserter("inserter", id = "d", tile_position = [+1, 2])

    # We can now do this just fine, using id in-place of entity_number
    inserter1.add_circuit_connection("red", inserter2)
    # And this will work as well, preserving the connection already made
    blueprint.add_entity(inserter1)
    blueprint.add_entity(inserter2)

In Blueprints, ``id``s are guaranteed to be unique:

.. code-block:: python

    blueprint.add_entity("inserter", id = "same")
    blueprint.add_entity("inserter", id = "same") # DuplicateIDError: 'same'

[What about outside of blueprints?]

Sometimes on regular structures like grids, you want to be able to use a number to easily access each index in the grid.
A good compromise in this case is to simply cast the index to a string and use that as the id:

.. code-block:: python

    blueprint = Blueprint()

    combinator = ConstantCombinator()
    for i in range(5 * 5):
        x = i % 5
        y = int(i / 5)
        combinator.tile_position = (x, y)
        combinator.id = str(i)
        blueprint.add_entity(combinator)

    for i in range(5 * 5):
        try:
            blueprint.add_circuit_connection("red", str(i), str(i + 1))
        except KeyError:
            pass

[snaking connection image]

Using strings also gives you more flexibility in general:

.. code-block:: python

    blueprint = Blueprint()

    combinator = ConstantCombinator()
    for y in range(5):
        for x in range(5):
            combinator.tile_position = (x, y)
            combinator.id = str(x) + "_" + str(y)
            blueprint.add_entity(combinator)

    for y in range(5):
        for x in range(5):
            current  = str(x)     + "_" + str(y)
            diagonal = str(x + 1) + "_" + str(y + 1)
            try:
                blueprint.add_circuit_connection("red", current, diagonal)
            except KeyError:
                pass
    
[diagonal connection image]

Entity IDs also shine particularly brightly when using Groups.
Managing connections between groups of entities would be a nightmare, even if every group had the same amount of entities.
With entity IDs, it's simpler, clearer, and more explicit:

.. code-block:: python

    from draftsman.classes import Group
    from draftsman.entity import ArithmeticCombinator, DeciderCombinator

