# Changelog
## **0.3.0**
* Unified all of the data into pickles instead of generating source files
    - (Still need to figure out module init)
* Updated `.gitignore` to avoid committing previously mentioned pickle files
* Added `warning.py` for warning specification
* Added lots of warnings and their messages
* Renamed `errors.py` to `error.py` to match the new `warning.py`
* Renamed all Errors to have the 'Error' suffix, renamed a few
* Added `DraftsmanError` and `DraftsmanWarning` so you can catch any specific error or warning with them
* Made the testing suite compatable (or, at least *more* compatable) with mods
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