# Changelog
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