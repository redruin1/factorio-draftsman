# factorio_blueprint_tools
Python module for making Factorio blueprints.

#### Test
`python -m unittest discover`

### Features
* Modern and up to date
* Easy installation
* Intuitive API
* Verbose Errors and Warning
* Rigorous test suite
* Mod support

## TODO
* Finish `entity.py`
    * Fix entity dimensions being incorrect
    * Split some of the Mixins to be a little more compartmentalized
    * Make sure the Entity classes themselves don't need to be split
    * Extract Recipe data (according to the assembling machine)
    * Extract Instrument data (according to the programmable speaker)
    * Add all the hidden categories (`Loader`, `InfinityContainer`, etc.)
    * Handle 8-way rotation placement a little better
    * Properly handle defaults to prioritize space a little better
    * Test with mods
    * Errors + Warnings
* Finish `blueprint.py`
    * Big cleaning/refactoring
    * Finish `BlueprintBook`
    * Test with mods
    * Errors + Warnings
* Add extra features
    * **COMPLETE TESTING SUITE**
    * Think about the best way to handle generated data 
    * (Re)Add entity groups and their functionality (EntityLike class)
    * Specify Rails via nodes/beziers instead of manually placing *every* rail
    * Maybe add a `CombinatorCell` EntityLike?
    * Backport / make sure it works with python 2.7 and previous versions of Python 3
* Look into lua binding
    * Some script to convert the Python code, or backport to C and compile 2 libraries?