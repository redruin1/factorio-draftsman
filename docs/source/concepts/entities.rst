.. _handbook.entities.differences:

Entities
========

Entity IDs
----------

Draftsman allows you to access the ``entities`` lists of any :py:class:`.EntityCollection`, allowing you to access ``Entity`` instances that are already placed inside a Blueprint, so you can modify them on the fly:

.. code-block:: python

    blueprint.entities.append("inserter")
    blueprint.entities.append("inserter", tile_position=(1, 0))

    blueprint.entities[0].read_hand_contents = True # The first inserter?

However, using numeric index to access an entity is often cumbersome, due to the fact that its position can rapidly change, and that the number itself is rarely descriptive of the entity you're trying to access.

Instead, Draftsman allows you to specify string IDs to entities to provide more meaning to what they are, and then access them by those string IDs:

.. code-block:: python

    blueprint.entities.append("inserter", id="first_inserter")
    blueprint.entities.append("inserter", id="second_inserter", tile_position=(1, 0))

    blueprint.entities["first_inserter"].read_hand_contents = True # Ah, the first inserter! 

In Blueprints, IDs must be unique, or else a :py:exc:`.DuplicateIDError` will be raised:

.. code-block:: python

    blueprint.entities.append("inserter", id="same")
    blueprint.entities.append("inserter", id="same") # DuplicateIDError: 'same'

    # Outside of blueprints, this rule is only enforced when added to a 
    # blueprint with the id already taken
    outside_inserter = Inserter("inserter", id="same")
    blueprint.entities.append(outside_inserter) # DuplicateIDError: 'same'

.. _handbook.entities.entity-associations:


``Entity`` vs. ``EntityLike``
-----------------------------

In Draftsman, for extensibility there is a distinction between the ``Entity`` and ``EntityLike``.
The basic distinction is this:

* ``Entity`` is for any entity type **understood by Factorio**, which includes all vanilla and modded entities; basically anything that can be actually placed in-game.
* ``EntityLike`` is for any custom entity type for scripting functionality, and is defined more broadly and flexibly to accomodate this.

If the object is an instance of ``Entity``, the implicit assumption is that it must exist in Factorio in some form or another; Think assembling machines, pumps, drills, as well as entities that tend to act as frameworks for other entities, like :py:class:`.ElectricEnergyInterface`.

``EntityLikes`` are more flexible: EntityLikes can do anything, as long as it's ``get()`` method resolves itself to one or more ``Entity`` objects.
This ``get`` function allows an ``EntityLike`` that's placed inside a ``Blueprint`` to be exported properly in a format understood by Factorio.
A ``Group`` object is resolved to the entities it contains, a ``RailPlanner`` is resolved to the tracks it laid, etc.

This allows the user to specify user classes that do some useful function that can be specified in the abstract before being resolved to entities.
An examples could be a ``Grid`` class, that places a specific entity at an X and Y interval, such as for making large regular power grids:

.. code-block:: python

    from draftsman.classes.blueprint import Blueprint
    from draftsman.classes.entitylike import EntityLike
    from draftsman.entity import new_entity

    class Grid(EntityLike):
        """Regular grid of substations spaced at their max distance."""
        def __init__(self, entity_name="substation", position = (0, 0), dim = (1, 1), off = (18, 18)):
            super(EntityLike, self).__init__()

            self.entity_name = entity_name 
            self.position = position
            self.dimension = dimension

            if "direction" in kwargs: # Optional
                self.direction = Direction(direction)

        def get(self):
            """
            Return a list of entities evenly spaced apart when resolved inside a Blueprint.
            """
            out = []
            for j in range(self.dim[1]):
                for i in range(self.dim[0]):
                    entity = new_entity(
                        self.entity_name, 
                        tile_position=(i*self.off[0], j*self.off[1])
                    )
                    out.append(entity)

            # TODO: connect each entity to it's neighbour

            return out

    def main()
        blueprint = Blueprint()

        blueprint.entities.append(Grid("medium-electric-pole", dim=(2, 2), off=(5, 5)))

        # ...

        print(blueprint.to_string())


.. _handbook.entities.entity-merging:

Entity Merging
--------------

When playing Factorio, the game allows you to place certian entities of similar types on top of other entities, which combines their attributes in specific ways. As now intruduced in version ``1.0.0``, a subset of this behavior is now also supported in Draftsman.

To be more specific, *entity merging* is defined with the following criteria:

1. Be an instance of the same class (``Container``, ``TransportBelt``, ``ElectricPole``, etc.)
2. Have the exact same :py:attr:`~.Entity.name`
3. Have the same :py:attr:`~.Entity.id` (can be ``None``, but both must be ``None``)
4. Occupy the exact same :py:attr:`~.Entity.global_position`
5. Be facing the exact same :py:attr:`~.DirectionalMixin.direction` (if applicable)

.. NOTE::

    Entity merging does **NOT** include *replacing*, such as defined under Factorio's fast-replacable-group. This is why entity merging is described as a subset of Factorio's behavior, as replacing entities with entities with different names is not (currently) implemented.