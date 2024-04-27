# TODO

### Add `tiles` to Groups (somehow)
We could simply add a `tiles` list to `Group`, but this has some unintended consequences. See issue #118 for more info.

---
### Calling validate on a blueprint should validate all of it's child entitylikes and tiles (or should it?)

---
### A better way to filter specific errors (some further API additions to `ValidationResult`, likely)

---
### If `validate_assignment` on a blueprint is `True`, does that mean that an appended entity or tile should be validated? Should overlapping object warnings be issued?
Answer: split blueprintable validation and entitylist/tilelist validation and have them all be separate
It might be confusing at first, but this way every combination is possible.

---
### Redo validation (again)
Swapping to Pydantic was very illuminating in the benefits that it can provide:

* Ergonomic class definitions to define schemas (very nice)
* Being able to inject custom functions at any point of the validation process to massage inputs, discredit validation, and add new criteria (possibly on the fly!) This is probably going to be required by any further implementation going forward
* All of these validation functions are localized to the classes that use them, and everything is in one place; only a single method has to be called for any member modification.
* Validation backend is written in Rust for speed (tempting)

However, it is still not quite entirely perfect:

* RootModel syntax cannot be serialized if not in the correct model format (unacceptable, currently this is sidestepped but suboptimal)
* RootModel syntax is unwieldly; everything is accessed via it's `root` attribute and any methods that you would want to use on `root` have to be reimplemented in the parent class
* I HAVE to use RootModels if I want to be able to reliably validate these members (and ideally propagate their `is_valid` flags)
* Per instance validate assignment is not permitted (even though totally functional), meaning I have to use the model's backend which might be subject to change
* No in-built handling for warnings, which ideally would behave very similarly to errors as Pydantic currently implements them

Based on my search, I can't think of a validation library that has all of these features at once, implying that I would have to roll my own. I'm not really looking forward to this, and especially not to *testing* it, so if there is one out there please message me.

---

### Validation caching
Ideally, whether or not a entity or blueprint is considered valid can be retained as long as the entity does not change after validation. For example, if you validate a single entity, and then add that entity to a blueprint 1000 times, you only have to validate the attributes of the blueprint itself, since the entities are guaranteed to already be in a valid state. Ideally, each exportable object would have a `is_valid` attribute which would be set to false when an attribute is set, which can then be quickly checked in any parent
`validate()` function.

---
### Integrate with `mypy`

---
### Revamp the `add_x` data functions so that they support more features
* Inline sorting
* Support additional keyword arguments in line with the prototype documentation
* Perhaps there might be a way to redesign `env.py` such that it can use the data functions, encouraging code reuse

---
### Change all internal attribute accesses to use `["element"]` and `.get("element", None)` instead so that functionality should remain constant when importing dicts when `validate="none"`

---
### Add as many of the example programs to the test suite as possible
To help ensure that they're behaving correctly over any API changes, so they stay up-to-date

---
### `EntityList.clear()` has some bad side effects, investigate and fix
Might make sense to actually move all of the spatial detection code into `EntityList`

---
### Add constraints on `DeconstructionPlanner`
General constraints on parameters and inputs; what you can deconstruct, what you can't, etc.

--- 
### Improve docs for `Blueprintable` copying
See issue #117

---
### Write `__repr__` function for everything
For most of the commonly-used things this is already the case, but would be nice if every Draftsman object had a nice, user-readable formatted output.

---
### Write `dump_format` (and test_cases)
Do this not only for all the blueprintable types, but also each entity. In addition, include this output at the header of each documentation file, so people finally have a concrete reference for the actual blueprint string format
- Once that's done, maybe we can finally update the Factorio wiki to be up-to-date

---
### Reinvestigate making an entity's `tile_position` based off of it's `position`

---
### Make draftsman's prototypes match Factorio's prototypes exactly (for consistency's sake)
As of writing there are a number of classes and class types that differ due to python functionality; it might make sense to unify the two so that class `AssemblingMachine` inherits the same classes in Factorio as it does in Draftsman.
This could also fix a few things related to their inheritance...

---
### Make it so that you can change the name of an `Entity` if the two collision boxes match
This is very complex though, there's a reason I put this off

---
### Add warnings for placement constraints on rails, rail signals and train stops
In tune of Factorio-correctness, we want to issue warnings when things won't work properly in Factorio. Rail entities have a lot of positional and orientation constraints that must be followed in order for them to be properly placed. Currently, Draftsman doesn't warn the user if they place a train stop the wrong way, for example, so ideally it should.

---
### Reevaluate the diamond diagrams for inherited `Entity` subclass
The way inherited methods are specified in some prototypes are a little messy, since I'm treating most inherited classes as mixins, and their interaction with each other can get quite complex; needs a big-picture analysis to see if there are any improvements to be made

---
### Figure out exactly what determines if an `Entity` is flip-able or not
Reverse-engineer the game to figure out what exactly determines if the game will let you flip an entity. Less important for vanilla entities, moreso important for modded ones, as we have to figure it out dynamically

---
### Update documentation guide to reflect 2.0 changes

---
### More doctests
Doctests are great because they mean that the documentation will stay exactly up to date with the code it documents; I've been meaning to add more ever since I discovered the feature but I haven't quite gotten around to it yet

---
### Split documentation from docstrings so that each function has a more readable example
Documentation is currently written in [reStructuredText](https://docutils.sourceforge.io/rst.html), which looks great for the ReadTheDocs website, but less so when using type hinting in your code editor. All should be rewritten in a format which looks good in both, ideally without duplicating documentation in 2 separate places.

---
### Custom `data.raw` extraction and formatting?
Currently all the data being extracted from the Factorio load process is all "hard-coded"; you have to manually edit `env.py` in order to change what it extracts. This is alright for the maintainers of Draftsman as we can simply edit it if we need more/less information from `data.raw`, but what if the user wants some data from Factorio that Draftsman doesn't bother extracting? In this case Draftsman would benefit from a generic editable interface where people can configure and modify exactly the information they want from the game for whatever their purposes are.

---
### Perhaps add options for blueprint canonicalization
Ordering objects inside blueprints in regular ways for best compression, minimal git diff, etc.

---
### Add more examples
Should also probably subdivide the examples folder into subfolders like `rail`, `combinator`, `queries`, `misc`, etc.
And give each folder their own README.md that describes what each one does

---
### Investigate a Cython/Rust rewrite in efforts to make the library as performant as possible
Likely the last-most step, once all other feature requests and optimization passes are complete, to help squeeze as much out of the code-base as possible