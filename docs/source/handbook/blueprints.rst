Blueprints
==========

.. _handbook.blueprints.blueprint_differences:

Differences between a Blueprint object and a JSON dict
------------------------------------------------------

Blueprint classes have 2 attributes that are different than a static blueprint dict:

1. :py:attr:`.Blueprint.entities`
2. :py:attr:`.Blueprint.tiles`

Both of these are a :py:class:`.EntityList` and :py:class:`.TileList`, respectively.
Both lists have all of the normal methods you would expect from lists:

.. code-block:: python

    blueprint = Blueprint()
    blueprint.entities[0]           # __getitem__
    blueprint.entities[1] = ...     # __setitem__
    blueprint.entities.append(...)
    blueprint.entities.insert(...)
    blueprint.entities.reverse()
    blueprint.entities.sort()
    blueprint.entities.copy()
    # TileLists are largely the same:
    blueprint.tiles.append(...)
    # etc...

However, they also posess some extra functions. 
Like most other blueprint attributes, they are type-checked to only accept :py:class:`.EntityLike` and :py:class:`.Tile` objects:

.. code-block:: python

    blueprint.entities.append(20)   # TypeError: Entry in EntityList must be an EntityLike
    blueprint.tiles.append(30)      # TypeError: Entry in TileList must be a Tile

Their :py:meth:`~.EntityList.append` and :py:meth:`~.EntityList.insert` functions allow for a special shorthand, where you can specify the name of the entity you want to make followed by any keyword arguments (similar to :py:func:`.new_entity`). 
This works on both ``EntityList`` and ``TileList``:

.. code-block:: python

    from draftsman import Blueprint, Inserter, Tile

    blueprint = Blueprint()
    blueprint.entities.append("inserter", id = "test", tile_position = (14, 10))
    assert isinstance(blueprint.entities[0], Inserter)
    assert blueprint.entities[0].name == "inserter"
    assert blueprint.entities[0].id == "test"
    assert blueprint.entities[0].tile_position == {"x": 14, "y": 10}

    # Insert is also similar with an additional positional argument:
    blueprint.tiles.insert(0, "refined-hazard-concrete-left", position = (1, 1))
    assert isinstance(blueprint.tiles[0], Tile)
    assert blueprint.tiles[0].name == "refined-hazard-concrete-left"
    assert blueprint.tiles[0].position = {"x": 1, "y": 1}

    blueprint.entities.append("any old string") # InvalidEntityError: 'any old string'

The ``append`` and ``insert`` functions also have an optional ``copy`` parameter, which determines whether or not to copy the passed-in entity:

.. code-block:: python

    inserter = Inserter("fast-inserter", tile_position=(0, 1))
    blueprint.entities.append(inserter, copy=False)
    inserter.stack_size_override = 1
    assert inserter is blueprint.entities[-1]
    assert blueprint.entities[-1].stack_size_override == 1

Note that this only works for the non-shorthand version; the shorthand always creates a new entity instance.

``append`` and ``insert`` also have another optional parameter, ``merge``, which indicates whether or not to try and merge entities placed inside a :py:class:`.EntityCollection`:

.. code-block:: python

    inserter = Inserter("fast-inserter")

    blueprint.entities.append(inserter)
    blueprint.entities.append(inserter, merge=True) # This entity gets merged with the one above

    assert len(blueprint.entities) == 1

For more info on entity merging, see :ref:`handbook.entities.entity-merging`.

EntityLists can also be indexed by string if there is a matching entity with that ID inside of the EntityList:

.. code-block:: python

    blueprint = Blueprint()
    belt = TransportBelt("fast-transport-belt", id = "this works!")
    blueprint.entities.append(belt)
    assert blueprint.entities["this works!"].name == "fast-transport-belt"

This only works for entities because tiles have no IDs.

.. _handbook.blueprints.forbidden_entity_attributes:

Manipulating Entities inside of Blueprints
------------------------------------------

Giving the user direct access to the ``entities`` list allows for very clear and flexible code.
Sometimes, though, this flexibility can be a little *too* much. 
Consider the following illustration:

.. code-block:: python

    # Lets place a small power pole at the origin
    blueprint.entities.append("small-electric-pole")
    # Now, let's place a inserter right next to it
    blueprint.entities.append("inserter", tile_position = (1, 0))

    # What if we do this?
    blueprint.entities[0].name = "substation"
    # This:
    #   Now should raise an OverlappingEntitiesWarning because it intersects the inserter.
    #   Changes the dimensions of the entire blueprint.
    #   Might change the hashmap grid cells the entity is located in.
    #   Might introduce invalid data states where an entity now has attributes it shouldn't.
    # Also consider:
    #   What if we had a connection between an entity and we moved it out of it's maximum
    #   range? That should issue a ConnectionRangeWarning as well.
    #   What about Rail signals, that can only exist adjacent to a rail entity? If we 
    #   happen to move one to an invalid position, we should throw another warning on top of
    #   anything else.
    #   In fact, this can be generalized to any entity that has some kind of restriction
    #   on it; we need recheck all of these every time the object is altered!

Thats a lot of potential problems! 
Now, theoretically it should be possible to handle all of these cases properly, though handling them *elegantly* is a tougher problem.
Currently, Draftsman sidesteps this by simply preventing the modification of the entity's name after it has been created:

.. code-block:: python

    blueprint.entities[0].name = "substation" # AttributeError: can't set attribute 'name'

``entity.name`` is special in that it can intoduce data in the wrong entity, which is scary enough that I have disabled modification of it after initialization entirely. 
Others, such as ``entity.position`` *can* be modified, but not while they currently exist in an ``EntityCollection``.
Most attributes are not like this however, and the majority can be modified even when placed inside an ``EntityCollection``; only an important, select few are restricted in this way.
A complete list of all attributes that are 'guarded' like this and their reasons are provided below:

.. list-table:: Immutable Entity Attributes
    :header-rows: 1

    * - Attribute
      - Reason(s)
    * - ``entity.name``
      - * New entity could have data it shouldn't(!)
        * New entity dimension has potential to occupy other entities' space
        * New entity dimension might change dimensions of parent blueprint
        * Might exist in the incorrect hashmap grid cells

.. list-table:: Restricted Entity Attributes
    :header-rows: 1

    * - Attribute
      - Reason(s)
    * - | ``entity.position`` or
        | ``entity.tile_position``
      - * New position has potential to occupy other entities' space
        * New position might change dimensions of parent blueprint
        * Might exist in the incorrect hashmap grid cells
    * - ``entity.direction`` (if applicable)
      - * New direction (if non-square) might occupy other entities' space
        * New position might change dimensions of parent blueprint
        * Might exist in the incorrect hashmap grid cells

The proper way to deal with modifying these parameters on an entity is to remove it, change its attribute, and then re-add it:

.. code-block:: python

    blueprint.entities.append("small-electric-pole")
    blueprint.entities.append("inserter", tile_position = (1, 0))

    blueprint.entities.pop(0) # small-electric-pole
    power_pole = ElectricPole("substation")
    blueprint.entities.append(power_pole)
    # This raises the correct warnings and errors in a much more predictable way,
    # which makes the maintainer much happier :)