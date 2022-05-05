# Changelog
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