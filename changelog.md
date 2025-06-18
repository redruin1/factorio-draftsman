# Changelog

## 3.0.0
* Updated `factorio-data` to version `2.0.49` (latest)
* Updated `compatibility/defines.lua` to `2.0.49` (latest)
* Switched from `pydantic` to `attrs`; 
    * A much better fit for Draftsman's scope, much more flexible, and much less boilerplate to maintain
    * Clearer distinction between loading steps:
        * Constructors are for initializing Draftsman objects
        * `from_dict()` and `from_string()` methods are for importing from raw JSON/Blueprint String
        * `to_dict()` and `to_string()` methods are for exporting to raw JSON/Blueprint String
        * Hooks are defined outside of the class scope which convers the raw JSON format to the internal Python object form
        * This now means that the Python objects are not strictly tied to the JSON format, which means they can deviate for ease of use/performance reasons
        * Conversion functions are separate from validation, meaning shorthands can be resolved even with validation functions turned off
* Draftsman entities can now handle importing/exporting between Factorio 1.0 and Factorio 2.0 blueprint string formats
    * Simply specify `version=(1, 0)` or `version=(2, 0)` in any of `to/from_dict()` or `to/from_string()` methods
    * While serialization/deserialization is correctly implemented, *migration* from an old to new string is not (fully) implemented, and so some parts will still have to be done manually
        * For example, Draftsman will not convert `"filter-inserter"` into `"fast-inserter"` for you
* Added tests to validate the exported formats of all objects match the above JSON schemas, on both game versions
* Added `draftsman.constants.Inventory` which is part of defines
* Changed the constant `ValidationMode.NONE` to be the more explicit `ValidationMode.DISABLED`
* Removed the `validate_assignment` attribute entirely
    * Instead, validation is now on a global flag (until there is a good reason for it not to be); makes things much simpler
    * Global flag can be acquired with `draftsman.validators.get_mode()` and set with `draftsman.validators.set_mode(...)`
    * `set_mode()` can also be used as a context manager:
        ```py
        # Default validation level is `STRICT`
        assert draftsman.validators.get_mode() is ValidationMode.STRICT

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            # No validators are run inside this block
            assert draftsman.validators.get_mode() is ValidationMode.DISABLED

        # Validation state returns to whatever it was set before
        assert draftsman.validators.get_mode() is ValidationMode.STRICT
        ```
* Calling a objects `validate()` method is now guaranteed to also validate all of its children


## 2.0.3
* Updated `factorio-data` to version `2.0.48` (latest)
* Fixed #164 (Decider combinator example doesn't work)
* Merged vjanell's pull request:
    * Fix reversed operators in DeciderCombinator `__ge__` and `__le__` methods

## 2.0.2
* Updated `factorio-data` to version `2.0.45` (latest)
* Fixed #158 (Key "comparator" not found when exporting/importing Constant Combinator)
* Fixed #157 (Incompatibility with pydantic>=2.11)

## 2.0.1
* Updated `factorio-data` to version `2.0.41` (latest)
* Added `planets.get_surface_properties()` which grabs a dict of surface properties with valid defaults
* Added `Entity.surface_conditions`, which maps directly to the Factorio API `surface_conditions`
* Added `Entity.is_placeable_on()`, which returns false if an entity's `surface_conditions` prohibit their construction on a planet
* Added `utils.passes_surface_conditions()`, which acts as the abstract backend which runs `Entity.is_placable_on()` and `recipes.is_usable_on()`
* Added testing for `Asteroid Collector`
* Finished implementing features for `LogisticsContainer`s
* `quality` is now an accessible and modifiable attribute of `Entity`s
* Made `Container.inventory_size` proportional to the entity's `quality`
    * *(note that all quality modifiers are not yet available)*
* Merge RosieBaish's pull request:
    * Add logic to allow mods with different special characters
* Merge Gavinp's pull requests:
    * Add test for creating items with position
    * Add test for recycler `get_world_bounding_box()`
    * `draftsman` now prints usage/help on empty args.
* Fixed #142 (Logistics containers not importing properly)
* Fixed #121 (Support for Bob's Inserters)
* Fixed #151 (Severe Performance degradation when using `add_circuit_connection`)

## 2.0.0
* Updated `factorio-data` to version `2.0.28` (latest)
* Updated `compatibility/defines.lua` to `2.0.28` (latest)
* Updated all prototypes to match Factorio 2.0
* Added new prototypes in Factorio 2.0
  * `AgriculturalTower`
  * `AsteroidCollector`
  * `Car`
  * `CargoBay`
  * `CargoLandingPad`
  * `CurvedRailA`
  * `CurvedRailB`
  * `DisplayPanel`
  * `ElevatedCurvedRailA`
  * `ElevatedCurvedRailB`
  * `ElevatedHalfDiagonalRail`
  * `ElevatedStraightRail`
  * `FusionGenerator`
  * `FusionReactor`
  * `HalfDiagonalRail`
  * `LightningAttractor`
  * `RailRamp`
  * `RailSupport`
  * `SelectorCombinator`
  * `SpacePlatformHub`
  * `SpiderVehicle`
  * `Thruster`
* Removed command line utility `draftsman-update`
* Added command line utility `draftsman` with multiple subcommands
    * `draftsman update ...` for the original functionality of modifying a Factorio environment 
    * `draftsman list` to list all mods detected under a particular environment
    * `draftsman enable/disable ...` enables or disables one or more mods
    * `draftsman factorio-version` reports or sets the version of Factorio's data
    * `draftsman version` reports Draftsman's own semantic version
    * Write `draftsman -h` or `draftsman [command] -h` for more information
* Swapped from `schema` to `pydantic`
    * Format for specifying schemas is now much clearer
    * Both blueprintables and entities now share the same exporting code, overall making more sense
    * Can now create a JSON schema of any entity or blueprintable (by calling `Object.json_schema()`), which can be exported and used in any other program that reads JSON schema(!)
    * However, minimum Python version is now 3.7 to support type hints
* Switched from `unittest` to `pytest` (more features with similar syntax; `coverage run` still works the same)
* Changed the code to be primarily Python3 compatible with the new minimum version
* Added `extras` module which implements some handy new features:
    * Added `flip_belts(blueprint)` which flips all belt entities inside the blueprint (preserving continuity)
* Added a bunch of equivalent functions from the Factorio StdLib:
    * Added `opposite()`, `next()`, `previous()`, `to_orientation()`, and `to_vector()` to `Direction`
    * Added `Orientation` class, similar to `Direction`; comes with it's own suite of `__add__()`, `to_direction()`, and `to_vector()` helpers
    * Added `constants.Ticks` enumeration which contains `SECONDS`, `MINUTES`, `HOURS`, etc. stored as quantities of Factorio ticks
* Added `union`, `intersection`, and `difference` to `EntityList`, `TileList`, and `ScheduleList`
* Updated `Direction` to now be the Factorio 2.0 16-direction enum; use `LegacyDirection` for the old enumerations
* Added `TrainConfiguration`, which allows you to specify entire trains with strings like `"1-4-1"` and customize them on a per-car basis
* Added `WaitCondition` and `WaitConditions` objects which keep track of train station condition trees
    * `WaitConditions` can be combined using bitwise `and` and `or` in order to collect them into a `WaitConditions` object:
    * Added `WaitConditionType` and `WaitConditionCompareType` enumerations
* Added `Collection.add_train_at_position()` and `Collection.add_train_at_station()` to make placing trains easier
* Added `Collection.find_trains_filtered()` to allow users to search Blueprints/Groups for trains of particular types
* Added `RailPlanner` (finally)
* Added `data.fluids` module with some useful helpers
* Added `data.planets` module allowing you to access planet metadata for things like surface properties
* Added `data.items.fuels` which is dict of sets of item names that fall under their respective fuel categories
* Added data functions `signals.add_signal()`, `tiles.add_tile()`, `entities.add_entity()`, etc. which allow you to add entities on the fly (primarily for Factorio environment compatibility)
* Added `RequestItemsMixin` to `Locomotive`, `CargoWagon`, and `ArtilleryWagon`
* Added `unknown` keyword to all entity/tile creation constructs which allows the user to specify what should happen when draftsman encounters an entity it doesn't recognize
* Changed `InvalidEntityError` and `InvalidTileErrors` so that they now try to detect a similar tile/entity name and display that information to the user in the error message
    * For example, if you accidentally type `Container("wodenchest")`, it will realize you probably meant to type `Container("wooden-chest")` and suggest that to you instead
* Added a bunch of new documentation to document the above
* Added a bunch of new examples to test out the above new features
* Added a fixture that ensures that Draftsman is running a vanilla configuration before running tests, and exits if it detects that it is not the case.
* Added a new command line option for `draftsman-update` `--lua-version`, which prints the version of Lua currently being used for debugging compat issues
* Added a README.md to the `examples` folder which provides short descriptions for all of the examples
* Integrated aforementioned examples into the test suite
* Removed the `area`, `tile_width`, and `tile_height` properties from `Blueprint`, which have been replaced with `get_world_bounding_box()` and `get_dimensions()`
    * These attributes are no longer cached in the blueprint and have to be recalculated each time such information is desired
    * However, this means that it only has to be calculated when the user actually wants it, instead of every time a user adds a new entity/tile to a blueprint
    * The user has a better idea of when they can cache the blueprint's dimension to reduce calculation, so it's deferred to the user
    * By making them functions it also makes it abundantly clear that calling them is not likely `O(1)`
* Added the `get_first` method to the defaults for the name of every entity
    * This means that if a data configuration has zero entities of a particular type, using a default name will result in a palatable error instead of something cryptic
* Added `index` attribute to all `Blueprintable` types, which allows the end user to customize the index in a parent BlueprintBook manually
    (Still autogenerated based on list order if unspecified, but now *can* be overridden)
* Added data functions `signals.add_signal()`, `tiles.add_tile()`, `entities.add_entity()`, etc. which allow you to add entities on the fly (primarily for Factorio environment compatibility)
* Fixed a bunch of warts in the API:
    * Added the ability to modify `x` and `y` attributes of both `position` and `tile_position` and have each other update in tandem
    * Made it possible to rotate objects in parent `Collections` as long as they're either square or rotated such that they preserve their original footprint (akin to Factorio)
    * Added `__eq__` operators to pretty much all draftsman things (`Entity`, `EntityList`, `TileList`, `ScheduleList`, `Schedule`, `WaitConditions`, etc.)
    * Added more professional `__repr__` functions to pretty much all draftsman things as well
* Normalized all import filenames to use underscores consistently (potentially breaking change!)
* Finished up documentation on `DeconstructionPlanner`
* [PERF] Reduced memory consumption by up to ~80 percent(!) (This also made it quite a bit faster to boot)
* Made it so that default `collision_mask` keys are resolved at once at the data level when you call `draftsman-update`, so you can query `entities.raw` for the correct default value
* Bumped Lupa to 2.0 which allows me to specify Lua version 5.2 which Factorio uses (#50)
    * `draftsman-update` will issue a warning if it cannot specify the correct Lua version: It'll still try to load and may still work anyway, but it's not guaranteed to\
* Added `--factorio-version` command for `draftsman-update` which either displays the current Factorio version or sets it to a specific Github tag
* Patched InvalidModVersionError for now (#51)
* Removed `on_(tile/entity)_(insert/set/remove)` from all `EntityCollection` and `TileCollection` classes
* Removed `on_(insert/set/remove)` from all `Entity` implementations as well (they were not used and are replaced with better things now)
* Renamed `data` member to `_root` member on `EntityList` and `TileList` (Internal reasons)
* Fixed issue #119

# 1.1.1
* Updated `factorio-data` to version `1.1.103`
* Merged RosieBaish's pull request:
    * Added an `extend()` function to `EntityList` along with notes about it's performance
* Fixed issue #101 (finally)

# 1.1.1
* Added a number of missing prototype objects that are blueprintable:
    * `SimpleEntityWithOwner`
    * `SimpleEntityWithForce`
    * `PlayerPort`
* Fixed an issue where color settings were not recognized in the settings stage (#103)
* Fixed issue loading IndustrialRevolution modpack (regression) (#98)

## 1.0.6
* Updated `factorio-data` to version `1.1.88`
* Updated `compatibility/defines.lua` to `1.1.88`
* Merged arpheno's pull request:
    * Fixed `Pump` so that it now correctly exports it's `direction`
* Merged SIGSTACKFAULT's pull requests:
    * Fix type annotation of `Tile.__init__()`
    * Fix type annotation of `BlueprintBook.insert()`
* `draftsman-update` is now (finally) able to load mods from folder directories instead of just zip archives
* `draftsman-update` will now prefer mods in folders instead of zip archives if one of each type present and they have the exact same ID and version (I think this matches Factorio, create an issue if it's not)
* Added `--report` command to `draftsman-update` that prints out a list of currently active mods and their versions (to aid in bug reports)
* Fixed Lua `defines` table not being defined by the time `factorio-data/core` runs (#85)
* Fixed UTF-8 BOM tokens not being properly stripped from all mod Lua files, resulting in issues when sending to Lupa (#84)
* Changed the Lua load process a whole lot for `draftsman-update`, hopefully behaving more predictably and causing no regressions

## 1.0.5
* Added `get_blueprintable_from_JSON()` and patched `get_blueprintable_from_string()` so that it no longer converts the string twice (accidentally)
* Fixed issue where integer `playback_volume` values on programmable speakers wasn't getting coerced to a float and failing validation (#72)
* Fixed Blueprintable objects not being correctly initialized from their constructor when JSON dicts were passed as an argument (#75)
* Fixed `OverlappingObjectsWarning` being incorrectly emitted when `Gates` overlap `StraightRails` (they now are only emitted if they're not perpendicular to each other) (#76)
* Fixed `ConstantCombinator` not recognizing the `is_on` member (#77)

## 1.0.4
* Updated `factorio-data` to version `1.1.80`
* Updated `compatibility/defines.lua` to `1.1.80`
* Merged louga31's pull request:
    * Fix recipes so that they correctly read either internal format
* Fixed an issue where not all entities were being assigned to `entities.flippable` (#61)
* Fixed mod dependency loading (hopefully) so that it should actually handle recursive requires across an arbitrary number of different mods (#70)
* Fixed an issue where required Lua files with a single prepended dot or slash would break the path resolution (#70)

## 1.0.3
* Updated `factorio-data` to version `1.1.76` (latest stable)
* Updated `compatibility/defines.lua` to `1.1.76` (latest stable)
* Merged penguincounter's pull request:
    * Fixed logistics requester and buffer chest signatures not having the correct `circuit_mode_of_operation` key
* Added a `dump_format()` method to entities that outputs a user friendly description of all of the possible key/value entries in the exported blueprint dict
    * Still needs to be done for Blueprintable; ideally there would be a `Exportable` parent class that would implement the madness
    * Also need to investigate faster validation options since schema is pretty slow; maybe we can unify and improve speed at the same time
* Added a `get_format()` method intended to get a readable formatted string (that can easily be autogenerated at the top of each entity in the documentation! Not yet but soon)
* Changed `_exports` dict to be both more user readable and only defined on a per class basis instead of a per instance basis (so memory usage should be down)
* Prepped `env.py` for when Lupa version 2.0 goes live (which will resolve #50)
* Fixed `"Mining_Drones_Harder"` mod not loading because of stray "__MACOSX" folder defined alongside (#55)
* Fixed `"FactorioExtended-Plus-Logistics"` not loading due to internal file titled `__init__.lua` (#56)
* Fixed `env.extract_entities().categorize_entities()` to `get` flags instead of assuming they exist (`"flags"` set is common but optional)

## 1.0.2
* Added `UpgradePlanner` and `DeconstructionPlanner` (#40)
* Created an abstract class `Blueprintable` which now implements `Blueprint`, `BlueprintBook`, `UpgradePlanner`, and `DeconstructionPlanner` to increase code reuse
* Added `description` attribute to `Blueprint` and `BlueprintBook` (#41)
* Changed the behavior of `draftsman-update` to normalize all mod names to have no spaces (probably not perfect, but should work for now) (#49)
* Added a `--path` argument to `draftsman-update` so you can specify exactly where to load mods from instead of only the installation directory (#49)
* Draftsman now distributes with a vanilla set of pickle data files, so you no longer need to run `draftsman-update` on first install (suggestion from rpdelaney)
* Rolling Stock (Locomotives and Wagons) should now have proper collisions that are based on their `orientation` and issue correct warnings (#47)
* Updated the documentation around `draftsman-update` to make it more clear and reflect recent changes
* Updated all `Blueprintable` documentation files such that they now include a plaintext representation of their JSON structure

## 1.0.1
* Updated `factorio-data` to version `1.1.65`
* Fixed #38 and #39

## 1.0.0
* Updated `factorio-data` to version `1.1.61`
* Added a `Vector` class to represent 2d positions, and changed most of the code to reflect this change
    * This is a breaking change, but it should be much more natural to access positions by attribute `x` and `y` instead of `["x"]` and `["y"]`
    * By specifying a class like this, custom operators are allowed such as vector math, which means that offsetting positions and other operations have become much easier as a result
    * `Vector` has a static member function `from_other()` that constructs a `Vector` object from all valid formats accepted in the past (`tuple`, `dict`, `list`, etc.) which is used in all standard functions, so you shouldn't have to change any of their signatures
    * `Vector` also has a `to_dict()` method to turn it back into it's dictionary format for exporting (`{"x": ..., "y": ...}`)
    * The `Vector` class is only used on the "outermost" layer due to performance reasons, internally the most common representation is still `list[float, float]`
* Added an abstract `Shape` class, along with two implementations: `AABB` and `Rectangle`
    * `AABB` and `Rectangle` are now used for issuing `OverlappingObjectWarning` 
* All functions that used to use `Sequences` or `list[list[float], list[float]]` have been changed to `Vector` and `AABB` respectively for user clarity
* Added another class: `CollisionSet`, which is a list of `Shapes` used for checking if two `Entity`s intersect one another
    * This was needed because curved rails have 2 collision boxes instead of a single one
    * Collision sets also support rotations, which means that rotations are automatically generated or specified manually for edge cases like rails
    * In essence, `CollisionSets` provide more flexibility for entity footprints on a per-entity-type (or even per-entity) level
* Added `find_entity_at_position()` so you can simply check for any entity in particular at a position instead of having to use fully-blown `find_entities_filtered` or the more-specific `find_entity()` function
* Abstracted `SpatialHashMap` to be an implementation of abstract class `SpatialDataStructure`, which will allow for different implementations such as quadtrees or other algorithms if they happen to be more performant than hash-mapping (For now all `Collections` still use `SpatialHashMap` though)
* Renamed `entity_hashmap` and `tile_hashmap` to more generic `entity_map` and `tile_map` to reflect the above change
* Move almost all entity insert/set/remove logic to `EntityCollection.on_entity_insert`, `on_entity_set`, and `on_entity_remove`, which gets called from `EntityList.insert` and related 
* Added `on_tile_insert`, `on_tile_set`, and `on_tile_remove` to `TileCollection` to mirror the changes to `EntityCollection`
* Added `copy` keyword to `TileList.insert` and `TileList.append` to mirror `EntityList.insert` and `EntityList.append`
* Added Entity/Tile merging
  * Added `merge` keyword to both `EntityList.insert/append` and `TileList.insert/append`
  * Attempting to use `merge=True` keywords and `copy=False` will result in a `ValueError`, as this behavior is loosely defined (for now at least)
* Rails now properly issue `OverlappingObjectsWarnings`; Rails can overlap each other provided they don't have the exact same position + direction + type
* Another big documentation pass
* Split the `signatures.CONTROL_BEHAVIOR` into many sub implementations, which should improve both safety and (hopefully) performance
* Fixed #24, #25, #27, #32, #33, and #34

## 0.9.7
* Merged louga31's pull request
    * Rewrite of the `_shift_key_indices` in `EntityList` to make it faster using list comprehension
* Merged elswindle's pull request
    * Moved conversion of associations from `Blueprint.load_from_string` to `Blueprint.setup` so they always take place
    * Fixed `UndergroundBelt` `io_type` attribute not reading correctly from key `type`
    * Changed test case to account for this
* Added `DirectionalMixin` to `AssemblingMachine` (as technically it can have it in select circumstances)
* Fixed load conflict between `items` and `recipe` in `AssemblingMachine` (#23)
* Fixed `setup.py` so that it properly requires `typing_extensions` on versions of Python prior to 3.8 (#30)
* Fixed importing `Literal` so that it follows the above change (#30)
* Fixed an issue where `BlueprintBook` icons were not properly set and issued an incorrect warning (#31)

## 0.9.6
* Merged sposker's pull request
    * Fixed an bug where `IndexError` would be triggered on setting the final item filter slot
    * Updated `signatures.CONTROL_BEHAVIOR` to include the `send_to_train` key
* Merged elswindle's pull request
    * Dictionary Blueprints and BlueprintBook's are now properly converted to `Blueprint` and `BlueprintBook` objects when added to a `BlueprintableList`
* Fixed documentation for `FilterMixin.set_item_filters` that labeled `"name"` key as `"signal"`
* Made docs for `FilterMixin.set_item_filters` and `FilterMixin.set_item_filter` more clear
* Changed `signals.raw` to actually be the extraction from `data.raw` so people can query the order strings and other information (#17)
* Sorted `signals.raw` according to signal-processing order (virtual -> fluid -> item) instead of item sort order (#17)
* Added `signals.type_of` as a more specific structure to fulfill the old functionality of `signals.raw` (#17)
* Changed the functionality of `ConstantCombinator` so that attempting to set one of it's signals to a pure virtual signal results in a `DraftsmanWarning` (because for some grotesque reason Factorio actually allows this)
* Renamed `InvalidConnectionError` to more general `InvalidAssociationError` and updated documentation
* Removed requirement for `Groups` to have an ID associated with it (this was required in the past, but is no longer necessary)
* Fixed unable to find connectable entities when calling `Blueprint.generate_power_connections()` on blueprint that contained `Groups` (#19)
* Added the capability to specify connections based on entity reference as well instead of just ID or index (`[add/remove]_power_connection`, `[add/remove]_circuit_connection`) (#19)
    * Made these functions issue `InvalidAssociationError` when attempting to connect two entities that lie outside of the `EntityCollection`
    * Added recursive `__contains__` function to `EntityList` to facilitate the above
* Fixed copying of entities between `Blueprints` and `Groups` (#20)
* Added capability to deepcopy `Entities`, `Groups`, and `Blueprints`, with appropriate errors
* Added capability to set the `entities` of a `Blueprint` or `Group` to another `Blueprints` or `Groups` `entities` (#16)
* Added optional `string` keyword for the constructor of `Group` so you can import a blueprint string directly into a group instead of having to create a "scratch" `Blueprint`

## 0.9.5
* Added `keywords` to `setup.py`
* Added `__contains__` function to `Blueprint` (I thought it was inferred from `__getitem__`, whoops) (#14)
* Added `defines.lua` as a more comprehensive solution to the Factorio `defines` issue (#15)
* Added distinguishing between multiple versions of the same mod; the latest mod is always preferred, with warnings for duplicates issued (#15)
* Started work on `RailPlanner`
* Other minor documentation changes
* Fixed the old repo link in `setup.py`
* Fixed #13:
    * Implemented the functionality according to the game, preserving Factorio safety
    * Added the new list `pure_virtual` signals to `draftsman.data.signals` for ease of access/iteration
    * Updated documentation to reflect these changes
* Moved initialization of `Blueprint.area` attribute before loading entities in `Blueprint.setup()` (#14)

## 0.9.4
* Added the capability to display any logged messages to during `draftsman-update` with the command line argument `-l` or `--log`
* Added `prep.py` to prepare releases more automatically so I don't miss steps like a fool (maybe I'll integrate something like poetry in the future)
* Updated `env.py` to create the `factorio-mods` folder if it doesn't exist, in case the user accidentally deleted it
* Updated `env.py` so that everything is now sorted (mostly) properly
* Updated readme to point to related Alt-F4 article
* Updated `requirements.txt` to include `build` for development
* Changed the manner in which sort items are searched in `env.py` (related to issue #9)
* Changed the manner in which the order of items are determined so there's less redundancy
* Changed `normalize_module_name` from non-digit characters to alphanumeric characters (duh!) (#11)
* Changed `normalize_module_name` to distinguish between "slash" paths and "dot" paths and only convert "dot" paths if found (#11)
* Added more duct tape to the local file requiring issue machine (#11)
* Removed `temp.py` from GitHub distribution, it was only really intended as scrap paper for me
* Fixed #10
* Fixed #12

## 0.9.3
* Fixed #9

## 0.9.2
* Added `signals` attribute to `ConstantCombinator`, which aliases `control_behavior["filters"]`
* (Re)Added circuit attributes back to `ArithmeticCombinator` and `DeciderCombinator`
* Minor docs fixes
* Bugfix: resolved #6
* Bugfix: resolved #8 (At least for now, current behavior should be more predictable)
* Also cleaned and documented the `update` process in `env.py` to make it a little clearer exactly what's going on, and trimmed the fat

## 0.9.1
* Updated `factorio-data` to `1.1.58`
* Added description of `control_behavior` attribute structure to `docs/source` folder
* Added read-only `global_position` property to `SpatialLike`; allows for efficient querying of an objects root-most position
* Added `SpatialHashMap.get_all`
* Added `utils.flatten_entities` since it's used in a number of places
* Added a `ItemCapacityWarning`, issued when `*Container` objects request items that exceed their inventory size
* Added `entities.flippable` to hold whether or not each entity can be flipped or not (tentative, still WIP)
* Integrated `entities.flippable` into `Entity` class, as well as `Transformable`
* Updated `tox.ini` to use `--no-mods` on `draftsman-update`
* Reworked `SpatialHashMap` and `get_area` to use `global_position` instead of `position`
* Reworked `RequestItemsMixin` and added it to more prototypes
* Split `ModuleSlotsMixin` from `RequestItemsMixin` to compartmentalize more
* Adding science pack item requests to a `Lab` no longer raises a warning (works with any lab)
* Made `set_x_filter` code more consistent across different prototype filter types
* Added folder loading to `draftsman-update`
* Documentation format fixes/additions
* Bugfix: Fixed the local paths that now point from `factorio-draftsman` instead of `factorio-draftsman/draftsman` in `draftsman-update` for folders
* Bugfix: Changed Lua file requiring so that it makes (somewhat) more sense; Honestly the whole thing is pretty fricking scuffed, and needs a redo
* Bugfix: Fixed `OverlappingObjectsWarning` occurring when placing two groups with the same local coordinates but different global coordinates in an `EntityCollection`
* Bugfix: Fixed Maximum recursion depth errors when running `examples/item_stack_signals.py` with large modpacks with many items; this should no longer occur period
* Bugfix: Split `index_dict` in `env.extract_items` to `group_index_dict` and `subgroup_index_dict`
* Bugfix: Encapsulated `order` swapping in `env.get_order` with a `try except` block

## **0.9.0**
* Officially added to PyPI (in beta state for the foreseeable future)

## **0.8.5**
* Finished first pass of documentation
* Added `factorio_version_testing.py`, which tests against prior versions of Factorio
* Draftsman is validated to work with versions of Factorio >= 1.0.0
* Added `Association`, which is a loose wrapper around `weakref` and takes care of the association problem
* Added docs for `Association`
* Added `--no-mods` flag to `draftsman-update` that just loads the base mod (why didn't I do this before)

## **0.8.0**
* Added a *whole lot* of documentation, or a first pass at least
* Updated the quick-start with updated information
* Setup a GitHub workflow to automatically upload code coverage for the badge
* Split the `ModeOfOperation` enumeration into `InserterModeOfOperation` and `LogisticModeOfOperation`
* Going to attempt to get Docs integration and passing
* Fixed ``draftsman-update`` greedy module name regex

## **0.6.0**
* First public release!
* Added `Groups`(!)
* Added the `1KiB_sector_ROM.py` example to illustrate `Group`s and `rail_planner_usage.py` for `RailPlanner` (`RailPlanner` is not implemented yet)
* Added `ltn_train_stop.py` example
* Lots of cleaning and formatting, though there's still many cases to analyze
* Added support for command line arguments with `draftsman-update` (currently only `--verbose`)
* updated `requirements.txt`
* Build system appears to be working as desired

## **0.5.0**
* Backported to Python 2.7; tested via `tox` that it works with latest version of Python 2 and 3
    * (Should work with every version between, but I'm too lazy to test right now)
* Got everything prepared (I think) for building and ultimately distribution
* Fixed `setup.py` so that it should work with all versions greater than 2.7 (as well as requirements.txt)
* Added entry-point `draftsman-update` that must be called after installation to initialize the module
* Lots of general folder restructuring (mainly moving everything needed into the module folder)
* Renamed `blueprint.py` to `blueprintable.py`
* Formatted everything using `black`
* Updated readme
* Updated examples
* Removed some redundant files

## **0.3.5.2**
* Split all of the mixins into their own files, as well as Entity, EntityLike, Group, etc.
* Added the `SpatialHashMap` structure for Blueprints to speed up `find_entities` and `find_tiles`
* Added lots of utility functions related to `SpatialHashMap`
* Changed Blueprint `entities` and `tiles` to `KeyList` instead of `list`
* Added Blueprint warnings

## **0.3.5.1**
* Changed ALL of the setters to use properties because I didn't know Python properties _existed_
* Revised test cases to match this revelation

## **0.3.0**
* Unified all of the data into pickles instead of generating source files
    - (Still need to figure out module init)
* Updated `.gitignore` to avoid committing previously mentioned pickle files
* Added `warning.py` for warning specification
* Added lots of warnings and their messages
* Renamed `errors.py` to `error.py` to match the new `warning.py`
* Renamed all Errors to have the 'Error' suffix, renamed a few
* Added `DraftsmanError` and `DraftsmanWarning` so you can catch any specific error or warning with them
* Made the testing suite compatible (or, at least *more* compatible) with mods
* Added LogisticActiveContainer and LogisticPassiveContainer to complete the logistic suite
(I think its clearer this way rather than treating them as containers)
* Hundreds of other small changes

## **0.2.1:**
* Finally finished entity testing (for now, reworks are coming)
* Split all of the entity definitions into their own file (much clearer)
* Added `image_converter.py` example
* Updated all other examples
* Changed data loading for items and entities to use pickle instead of writing
source files (the rest need to be done like this I think)

## **0.2.0:**
* Renamed the package from "factoriotools" to the more succinct and pythonic "draftsman" 
* General folder structure rework for both the package itself as well as testing
* Started the behemoth that is going to be Entity and Blueprint testing suites
* Added `.coveragerc` for coverage configuration
* Added this changelog

## **0.1:**
* Initial version