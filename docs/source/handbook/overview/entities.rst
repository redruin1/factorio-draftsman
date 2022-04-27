Entities
==========

Entities are organized roughly equivalently to the types of `Prototypes <https://wiki.factorio.com/Prototype/EntityWithOwner>`_ found in Factorio.
Only the entity types that are blueprintable are extracted, and most are identical in name and purpose.
There are a few notable exceptions:

1. Factorio ``Inserter`` is split into two classes, Draftsman ``Inserter`` and ``FilterInserter``.
2. Factorio ``LogisticContainer`` is split into its five subtypes, ``Passive``, ``Active``, ``Storage``, ``Requester``, and ``Buffer``.
3. Factorio ``AmmoTurret``, ``ElectricTurret``, and ``FluidTurret`` are joined together in Draftsman as the ``Turret`` class.

In Factorio, there are also a number of abstract prototypes that exist to collectivize similar entity types; ``CraftingMachine`` superclasses ``AssemblingMachine``, ``RocketSilo``, and ``Furnace``, for example.
Currently, Draftsman does *not* mimic these intemediary classes, though in the future it might be a good idea to implement classes more directly in-line with what Factorio defines.

Entity Attributes
-----------------

Most attributes on entities are implemented as properties with custom getters and setters.
This allows for inline type checking, as well as ensuring that certain values are read only and not deletable.

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

Entity Dimensions
-----------------

TODO

Entity IDs
----------

In normal Factorio blueprint strings, associations between entities are usually indicated by ``entity_number``, which is the index of the entity in the internal ``entities`` list.
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

    blueprint.entities.append("inserter", id = "a", tile_position = [-1, 0])
    blueprint.entities.append("inserter", id = "b", tile_position = [+1, 0])

    # These ids are always associated only with the entities that possess them,
    # regardless of their position or orientation within the blueprint's entity
    # list
    blueprint.add_circuit_connection("red", "a", "b")

    inserter1 = Inserter("inserter", id = "c", tile_position = [-1, 2])
    inserter2 = Inserter("inserter", id = "d", tile_position = [+1, 2])

    # We can now do this just fine, using id in-place of entity_number
    inserter1.add_circuit_connection("red", inserter2)
    # And this will work as well, preserving the connection already made
    blueprint.entities.append(inserter1)
    blueprint.entities.append(inserter2)

When exporting to Factorio, string IDs are converted to their numeric index just in time.

.. Note::

    When importing an already made Blueprint string, ID information is lost even with blueprints created by Draftsman.
    If you give an entity a custom ID, export it, then re-import it into a blueprint, attempting to access that entity with that ID will result in a `KeyError`.
    On these loaded blueprints, connections between entities are preserved as numbers, which makes them volatile for the reasons described above.
    Thus, if you are importing blueprints from a string that has connections already made that you would like to preserve, it's recommended that you only append to that blueprint's entities in order to preserve their internal order.

In Blueprints, IDs are guaranteed to be unique:

.. code-block:: python

    blueprint.entities.append("inserter", id = "same")
    blueprint.entities.append("inserter", id = "same") # DuplicateIDError: 'same'

    # Outside of blueprints, this rule is only enforced when added to a 
    # blueprint with the id already taken
    outside_inserter = Inserter("inserter", id = "same")
    blueprint.entities.append(outside_inserter) # DuplicateIDError: 'same'
    

Sometimes on regular structures like grids, you want to be able to use a number to easily access each index in the grid.
A good compromise in this case is to simply cast the index to a string and use that as the ID:

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

``Entity`` vs. ``EntityLike``
-----------------------------

The Draftsman inheritance diagram looks something like this:

[inheritance diagram]

In Draftsman, for extensibility there is a distinction between the Entity and EntityLike.
The basic distinction is this:

* ``Entity`` is for any entity type **understood by Factorio**, which includes all vanilla and modded entities.
* ``EntityLike`` is for any custom entity type for scripting functionality.

If the object is an instance of ``Entity``, the implicit assumption is that it must exist in Factorio in some form or another; Think assembling machines, pumps, drills, etc.
``EntityLikes`` are more flexible: EntityLikes can do anything, as long as it resolves itself to one or more ``Entity`` objects when exported while inside a Blueprint.
For example, say I'm working with combinators and I have a common design where I link a whole bunch of constant combinators in a regular grid, like so:

[combinator image]

You can encapsulate this design with something like this:

.. code-block:: python

    from draftsman.classes.entitylike import EntityLike
    from draftsman.constants import Direction

    class CombinatorCell(EntityLike):
        """Regular grid of constant combinators populated with data and linked together."""
        def __init__(self, name="constant-combinator", position = (0, 0), dimension = (1, 1), **kwargs):
            # Name of the constant combinator, can be substituted with a modded one if desired
            self.name = name 
            self.position = position
            self.dimension = dimension

            if "direction" in kwargs: # Optional
                self.direction = Direction(direction)

            # Keep a list of combinators
            self._combinators = []
            for 

        

        def to_dict(self):
            """
            Called when converting to a blueprint string. Must return a valid 
            dict or list of valid dicts.
            """
            out = []
            for combinator in self._combinators:
                out[]
