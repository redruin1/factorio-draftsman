=======================
Draftsman's Environment
=======================

What is Draftsman's "Environment"?
==================================

In order to make creating/modifying blueprint strings as seamless and convenient as possible, Draftsman desires information about the items, entities, tiles, signals, and all other things it interacts with. 
Having this information allows Draftsman to do convenient things for you, such as automatically deducing the type of an entity from just it's name, creating full signal objects from just strings, issue warnings if you put productivity modules in a machine who's recipe cannot recieve productivity, suggest that you actually meant "wooden-chest" when you accidentally type "woden-chest", and so on. 
Because none of this information is encoded in the blueprint strings themselves, it means that if this information is going to be provided, it must come from an external source.

Fortunately, Wube graciously provide the `factorio data <https://github.com/wube/factorio-data>`_ repository, which stores (almost) all of the Lua files necessary to run the data-lifecycle from scratch. 
Draftsman uses `Lupa <https://github.com/scoder/lupa>`_ to create a Lua instance to simulate to the load process as accurately as possible, producing a ``data.raw`` table just as the regular game would.
Draftsman then extracts specific sections (since Draftsman only desires portions), which are then stored in a number of pickle files located in the ``site-packages/draftsman/data`` folder. The data stored here is termed Draftsman's "environment", as it holds all of the contextual metadata that Draftsman uses to facilitate the above features.

By default, Draftsman comes shipped with a set of pregenerated data, so a new installation does not necessarily need to run the lifecycle immediately after installation.
However, this information does not automatically update, and must be initiated to do so :ref:`at the user's request <how_to_update>`.
Additionally, the format of these files are not given any gurantee to remain consistent across Draftsman or Factorio versions, so periodically updating your environment is never a bad idea.

Having Draftsman be so tied to this generated environment has pros and cons. 
On one hand, being able to access Factorio's data nigh-natively is immensely useful, and makes Draftsman a robust solution for all kinds of problems:

.. doctest::

    >>> from draftsman.entity import Container

    >>> # For example, if you ever want to know anything about wooden-chest, you can 
    >>> # just check it's prototype, which is literally it's `data.raw` entry:
    >>> chest = Container("wooden-chest")
    >>> chest.prototype.keys()
    dict_keys(['name', 'type', 'collision_box', 'flags', 'collision_mask', 'selection_box', 'icon', 'picture', 'close_sound', 'icon_draw_specification', 'inventory_size', 'corpse', 'minable', 'damaged_trigger_effect', 'dying_explosion', 'fast_replaceable_group', 'circuit_wire_max_distance', 'circuit_connector', 'impact_category', 'open_sound', 'surface_conditions', 'max_health'])

    >>> # If you have a copy of the game installed, you can use this info to load
    >>> # this entity's sprite, such as for rendering blueprints:
    >>> chest.prototype["picture"]
    {'layers': [{'width': 62, 'scale': 0.5, 'shift': [0.015625, -0.0625], 'height': 72, 'priority': 'extra-high', 'filename': '__base__/graphics/entity/wooden-chest/wooden-chest.png'}, {'width': 104, 'scale': 0.5, 'shift': [0.3125, 0.203125], 'draw_as_shadow': True, 'height': 40, 'priority': 'extra-high', 'filename': '__base__/graphics/entity/wooden-chest/wooden-chest-shadow.png'}]}


On the other hand, having such a tight integration with your environment can lead to problems when the desired environment differs from the one you currently have.
The classic example of this is attempting to import an old Factorio blueprint string under a modern environment:

.. doctest::

    >>> from draftsman.data import mods
    >>> from draftsman.blueprintable import Blueprint

    >>> # Here, our configuration is modern
    >>> assert mods.versions["base"] == (2, 0, 49, 0)

    >>> # Say we have an old blueprint string which contains one "filter-inserter".
    >>> bp_string = "TODO"

    >>> # In Factorio 1.0, this is a perfectly valid entity, but in 2.0 this entity
    >>> # no longer exists, so attempting to import it creates UnknownEntityWarnings
    >>> blueprint = Blueprint.from_string(bp_string)
    Warning
    
Draftsman knows how to parse the 1.0 string just fine, but because the data for ``"filter-inserter"`` does not exist under a Factorio 2.0 environment, it considers it entirely unknown and loads it as an ``Entity`` instance:

.. doctest::

    assert type(blueprint.entities[0]) is Entity

If you want to "migrate" this blueprint, you (currently) have to do it manually:

.. code-block:: python

    for entity in blueprint.entities:
        if entity.name == "filter-inserter":
            entity.name = "fast-inserter"
            entity = Inserter.from_dict(entity.to_dict())

This case is fairly demure, but this same problem arises with modded entity configurations. 
If somebody writes a script under a modded environment, that script may not posess enough information to properly run under a vanilla configuration.
You can mitigate this somewhat by using the :py:data:`draftsman.data.mods` module to query the fingerprint of the current environment:

.. code-block:: python

    from draftsman.data import mods

    # Only run this script if the current Factorio version is 2.X
    if mods.versions["base"] < (2, 0)
        raise ValueError("Cannot run this script on Factorio 1.0!")

    # Only run this script if a specific mod is present
    if "space-exploration" not in mods.versions:
        raise ValueError("This script expects the Space Exploration mod!")

Usually, unless you are intentionally trying to make scripts that are robust to different configurations, then the easiest way to resolve them is to simply update your current environment to match the one that the script expects.

.. _how_to_update:

How to Update the Environment
=============================

Draftsman provides 2 main ways to update the environment, depending on the particular needs of your circumstance. 

Console Entry Point
-------------------

The first (and usually simplest) way is to use the console script ``draftsman`` with the argument ``update``:

.. code-block:: text

    > draftsman update -h
    usage: draftsman update [-h] [-l] [--no-mods]

    Runs the Factorio data lifecycle using the data pointed to by `game_path`. All information that Draftsman needs will be extracted into pickle files located in the draftsman/data/ folder in the installation directory.

    options:
    -h, --help  show this help message and exit
    -l, --log   Display any `log()` messages to stdout; any logged messages will be ignored if this argument is not set.
    --no-mods   Prevents user mods from loading even if they are enabled. Official mods made by Wube (`quality`, `elevated-rails`, `space-age`) are NOT affected by this flag; those should be manually     
                configured with `draftsman enable|disable [official-mod]`


This command runs the data lifecycle once and then overwrites the pickle files with newly extracted data. 
This is convenient if you expect to write one or multiple scripts under the same environment, and only need to update or change your environment infrequently, such as when Factorio updates or when you add or remove a mod from a modlist.

For example, if a new minor version of Factorio releases, then you can use the following commands to update your factorio-data submodule, and then update your current environment to match the new release:

.. code-block:: text

    > draftsman -v factorio-data latest
    Current Factorio version: 2.0.48
    Different Factorio version requested:
            (2.0.48) -> (2.0.49)
    Changed to Factorio version 2.0.49
    > draftsman update --no-mods

This way you don't have to wait for Draftsman to update in order to recieve changes to Factorio's data.

For more information on how to use the ``draftsman`` utility, see `here <TODO>`. 

From Python Script
------------------

Sometimes it might be more convenient to update the environment directly from python script, however.
For the same functionality that the update script uses, you can use the methods located in :py:mod:`draftsman.environment`:

.. code-block:: python

    from draftsman.environment.update import update_draftsman_data

    # Exactly equivalent to calling `draftsman update`
    update_draftsman_data()

Neighbouring files in environment also provide mechanisms for decoding ``mod-settings.dat`` files, enabling/disabling mods, and more.

If there is some information that you need that Draftsman does not export for it's own purposes, Draftsman provides a convenience function you can call to return a complete loaded Lua instance you can manipulate:

.. code-block:: python

    from draftsman.environment.update import run_data_lifecycle

    lua_instance = run_data_lifecycle(
        game_path=..., # Game data path (either Factorio installation or Draftsman installation)
        mods_path=..., # Mod folder path
    )

    game_data = lua_instance.globals().data.raw
    
    # Extract yo shizz
    shizz = game_data[...]


Updating the Environment with Mods
==================================

Because we're emulating the game's loading process directly, including mods in Draftsman is exactly as easy as it is installing mods in Factorio. 
Doing so allows us to get the same level of validation that we get on vanilla entities as with modded ones; we can tell if a AAI warehouse's inventory bar exceeds it's inventory size, or if the wire connection distance between a Space Exploration pylon is too great for Factorio to connect, or that the entity ``"ltn-train-sotp"`` does not exist (and should be ``"ltn-train-stop"`` instead).

Including mods is usually a drag-and-drop operation, provided you have the mods already downloaded. 
Simply move the mods you want to install to the ``site-packages/draftsman/factorio-mods/`` folder, or point to a different ``mods_path`` using either the console utility or python script as illustrated above.

Draftsman's loading process was designed to perfectly match Factorio's.
However, this implementation is most likely not perfect, and ensuring correct behavior across all mods configurations possible is difficult to anticipate.
If you use Draftsman and come across an error that does not happen when loading the same mods with the same configuration in Factorio itself, please leave a issue `here <https://github.com/redruin1/factorio-draftsman/issues>`_ so I can track and resolve it.

How dependent is Draftsman on it's environment?
===============================================

The environment is not strictly necessary for Draftsman functionality; you can delete all pickle files in the data folder and the module will still run, though all of the features and benefits mentioned above will be absent. Any imported string will default to :py:class:`.Entity` instances, because there is no context to determine whether ``"some-entity"`` should be a :py:class:`.Container`, an :py:class:`.Inserter`, an :py:class:`.AgriculturalTower`, etc. However, if you're fine with these concessions, then there is nothing in Draftsman that isn't capable of coping with the lack of this contextual information, and if there is, it should be considered a bug and filed `here <https://github.com/redruin1/factorio-draftsman/issues>`_