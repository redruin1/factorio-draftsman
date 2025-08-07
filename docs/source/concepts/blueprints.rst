Blueprints
==========

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