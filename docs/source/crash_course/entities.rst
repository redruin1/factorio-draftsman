.. _handbook.entities.differences:

Entities
========

Entities are organized roughly equivalently to the types of `Prototypes <https://wiki.factorio.com/Prototype/EntityWithOwner>`_ found in Factorio.
Only the entity types that are blueprintable are extracted, and most are identical in name and purpose.
There are a few notable exceptions:

1. Factorio ``Inserter`` is split into two classes, Draftsman :py:class:`.Inserter` and :py:class:`.FilterInserter`.
2. Factorio ``LogisticContainer`` is split into its five subtypes, :py:class:`.LogisticPassiveContainer`, :py:class:`.LogisticActiveContainer`, :py:class:`.LogisticStorageContainer`, :py:class:`.LogisticRequesterContainer`, and :py:class:`.LogisticBufferContainer`.
3. Factorio ``AmmoTurret``, ``ElectricTurret``, and ``FluidTurret`` are joined together in Draftsman as the :py:class:`.Turret` class.

In Factorio, there are also a number of abstract prototypes that exist to collectivize similar entity types; ``CraftingMachine`` superclasses ``AssemblingMachine``, ``RocketSilo``, and ``Furnace``, for example.
Currently, Draftsman does *not* mimic these intemediary classes, though in the future it might be a good idea to implement classes more directly in-line with what Factorio defines.

Entity Attributes
-----------------

Most attributes on entities are implemented as properties with custom getters and setters.
This allows for a clean API, inline type checking, as well as ensuring that certain values are read only and not (easily) deletable.

.. code-block:: python

    container = Container()
    container.bar = "incorrect"  # Raises TypeError

However, there might be some circumstance where you would still like to use an Entity class, but would like to forgo Factorio-safety (or regular safety) for efficiency or some other functionality.
In that case, all *root level* attributes have their underlying value as their name prepended with a single underscore:

.. code-block:: python

    container = Container()
    container.bar = "incorrect"  # Raises TypeError
    container._bar = "incorrect" # Won't be a problem unless you import into Factorio

The not all attributes are specified as root level however, so specifying them becomes trickier.
Take the ``enable_disable`` attribute for example, which determines whether or not a condition is used to stop or start function of the Entity:

.. code-block:: python

    belt = TransportBelt()
    belt.enable_disable = "incorrect"  # Raises TypeError
    belt._enable_disable = "incorrect" # Raises AttributeError
    belt._control_behavior["circuit_enable_disable"] = "incorrect" # Fine until import

Here, you can see the ``enable_disable`` parameter is actually an optional entry in the entity's ``control_behavior`` dictionary, and the attribute simply aliases that value.
The structure of Entity classes are designed to live as close to possible to their exported state to reduce the amount of effort encoding and decoding them.
This means that if you want to go this route you'll need full knowledge of the internal structure of the entity in order to manipulate it properly, so it's advised that you 'know what you're doing'™.

Entity IDs
----------

Draftsman allows you to access the ``entities`` lists of any :py:class:`.EntityCollection`, allowing you to access ``Entity`` instances that are already placed inside a Blueprint, so you can modify them on the fly:

.. code-block:: python

    blueprint.entities.append("inserter")
    blueprint.entities.append("inserter", tile_position = (1, 0))

    blueprint.entities[0].read_hand_contents = True # The first inserter?

However, using numeric index to access an entity is often cumbersome, due to the fact that its position can rapidly change, and that the number itself is rarely descriptive of the entity you're trying to access.

Instead, Draftsman allows you to specify string IDs to entities to provide more meaning to what they are, and then access them by those string IDs:

.. code-block:: python

    blueprint.entities.append("inserter", id = "first_inserter")
    blueprint.entities.append("inserter", id = "second_inserter", tile_position = (1, 0))

    blueprint.entities["first_inserter"].read_hand_contents = True # Ah, the first inserter! 

In Blueprints, IDs must be unique, or else a :py:exc:`.DuplicateIDError` will be raised:

.. code-block:: python

    blueprint.entities.append("inserter", id = "same")
    blueprint.entities.append("inserter", id = "same") # DuplicateIDError: 'same'

    # Outside of blueprints, this rule is only enforced when added to a 
    # blueprint with the id already taken
    outside_inserter = Inserter("inserter", id = "same")
    blueprint.entities.append(outside_inserter) # DuplicateIDError: 'same'

.. _handbook.entities.entity-associations:

Entity Associations
-------------------

In normal Factorio blueprint strings, associations between entities are usually indicated by an integer, which is the index of the entity in the master blueprint's ``entities`` list.
Consider this hypothetical example, where we specify a circuit connection between two inserters:

.. code-block:: python

    blueprint = Blueprint()

    blueprint.entities.append("inserter", tile_position = [-1, 0]) # entity[0]
    blueprint.entities.append("inserter", tile_position = [+1, 0]) # entity[1]

    # Add a red wire connection between entity number 0 and entity number 1
    blueprint.add_circuit_connection("red", 0, 1)
    # Keep in mind, according to the blueprint string format "entity_id" is 1-indexed
    print(blueprint.entities[0].connections)
    # {'1': {'red': [{'entity_id': 2}]}}
    print(blueprint.entities[1].connections)
    # {'1': {'red': [{'entity_id': 1}]}}
    
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
What other options do we have?

We could iterate over each connection and fix any connections that change when the index of the entity it references changes, but this is hard to keep track of and computationally expensive.

We could store some immutable identifier, such as a string ID and use that as a connection point, but the same problem as before arises if you change the ID of an entity midway through. This also plays poorly with Groups, as the only way to keep connections consistent is to specify them in "global" terms, and change them every time their global position changes, which is also computationally expensive.

We could prohibit adding connections and wait until all entities are placed in a blueprint before making connections, but this is neither flexible nor desirable.

The solution that Draftsman uses is ``Associations``, which are loose wrappers around ``weakref.ref`` that point to other ``Entity`` objects.
By using direct references, we alleviate the problem of constantly changing connections every time the parent order changes, as the reference points to the data itself instead of a seperate marker:

.. code-block:: python

    # What you would actually see in Draftsman:
    blueprint = Blueprint()

    blueprint.entities.append("inserter", tile_position = [-1, 0])
    blueprint.entities.append("inserter", tile_position = [+1, 0])
    blueprint.add_circuit_connection("red", 0, 1)
    blueprint.entities.insert(1, "wooden-chest", tile_position = (0, 0))

    print(blueprint.entities[0].connections)
    # {'1': {'red': [{'entity_id': <Association to Inserter>}]}}
    print(blueprint.entities[1].connections)
    # {}
    print(blueprint.entities[2].connections)
    # {'1': {'red': [{'entity_id': <Association to Inserter>}]}}

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
    association = blueprint.entities[1].connections["1"]["red"][0]["entity_id"]
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

    print(blueprint.entities[0].connections)
    # {'1': {'red': [{'entity_id': Association to None}]}}

    print(blueprint.to_string())
    # InvalidConnectionError: 'inserter' entity at {'x': -0.5, 'y': 0.5} is connected to an entity that 
    # no longer exists

When exporting to Factorio, Associations are converted to their numeric index in the exported object to comply with the blueprint string format.
This process also works the other way; connections in imported blueprint strings are automatically converted to Associations on import:

.. code-block:: python

    # Basically identical to the blueprint above, two inserters connected with a red wire
    blueprint.load_from_string("0eNqdkN0KgzAMhd8l150s1bKtrzJk+BNGQaO0dUyk7762uxG8GbsJOeXkfGk2aIeFZmvYg97AdBM70PcNnHlyM6Q3v84EGoynEQRwM2bFjqwnC0HEvqc3aAy1AGJvvKFvRhbrg5exjU6Nx2kB8+TiwMSJFENKxEIJWEGfEKtCxfi4ElOXPC6ZMBVL/Z5gopKhDiGIA1X+RC3/pGKmxo/n8+jdNQW8yLrMkFesLjd5URWW6qxC+ABGinpP")

    print(blueprint.entities[0])
    # <Inserter>{'name': 'inserter', 'position': {'x': 311.5, 'y': -114.5}, 'connections': {'1': {'red': [{'entity_id': <Association to Inserter>}]}}}
    print(blueprint.entities[1])
    # <Inserter>{'name': 'inserter', 'position': {'x': 313.5, 'y': -114.5}, 'connections': {'1': {'red': [{'entity_id': <Association to Inserter>}]}}}


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

.. NOTE::

    The code above is provided as a simple example, and does not take into account things like overlapping entities.
    It's provided merely as a suggestion of the possiblities that structuring the module in this way provides.
    
.. WARNING::

    The code above is under heavy development while I try to make it more intuitive and easier for users to specify thier own custom classes.
    Keep this in mind that behavior might change drastically from version to version while I iron out the details.

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

.. WARNING::

    Due to technical reasons, merging power switches with power-wire connections (either "Cu0" or "Cu1") right now is **prohibited**. Bascially, these wire connections are abnormal in that they are 1-directional, which makes the order in which entities merge important to the final outcome of the merging result, as there is no way to check from the entity that is being pointed to back to the power switch that points to it to update it's connections. Fixing this is possible, but it requires a deliberate decision, and since this happens to be a minimal edge case and the merging of wire connections is already complex enough, this is the current behavior.