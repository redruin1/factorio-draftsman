# TODO

### Make all entities directional / request items
This seems to be the default behavior per [https://lua-api.factorio.com/latest/concepts/BlueprintEntity.html](https://lua-api.factorio.com/latest/concepts/BlueprintEntity.html)

### Remove classes:
* `LogisticsStorageContainer`, `LogisticsPassiveContainer`, ...

### Add `children` attribute to Blueprints/Groups, and use that to store nested Groups
This would make `entities` and `tiles` 1-dimensional lists again, and tree traversal would be more explicit
```py
blueprint = Blueprint()

blueprint.children.append(Group(id="blah"))

blueprint.children["blah"].entities.append("inserter", ...)
```

---
### Calling validate on a blueprint should validate all of it's child entitylikes and tiles (or should it?)

---
### A better way to filter specific errors (some further API additions to `ValidationResult`, likely)

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
### Display blueprint JSON schemas for all blueprintable types in the documentation
- Once that's done, maybe we can finally update the Factorio wiki to be up-to-date

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
### Update documentation guide to reflect ~~2.0~~ 3.0 changes

---
### More doctests
Doctests are great because they mean that the documentation will stay exactly up to date with the code it documents; I've been meaning to add more ever since I discovered the feature but I haven't quite gotten around to it yet

---
### Split documentation from docstrings so that each function has a more readable example
Documentation is currently written in [reStructuredText](https://docutils.sourceforge.io/rst.html), which looks great for the ReadTheDocs website, but less so when using type hinting in your code editor. All should be rewritten in a format which looks good in both, ideally without duplicating documentation in 2 separate places.

---
### Custom `data.raw` extraction and formatting?
In this case Draftsman would benefit from a generic editable interface where people can configure and modify exactly the information they want from the game for whatever their purposes are.

Alternatively, since Draftsman depends on `data.raw` when available more and more, perhaps the best solution (if performant enough) would be to simply extract the entirety of `data.raw`

---
### Perhaps add options for blueprint canonicalization
Ordering objects inside blueprints in regular ways for best compression, minimal git diff, etc.
- could probably integrate FATUL ()

---
### Add more examples
Should also probably subdivide the examples folder into subfolders like `rail`, `combinator`, `queries`, `misc`, etc.
And give each folder their own README.md that describes what each one does

---
### Investigate a Cython/Rust rewrite in efforts to make the library as performant as possible
Likely the last-most step, once all other feature requests and optimization passes are complete, to help squeeze as much out of the code-base as possible

---
### Extract constants from `defines.lua`
This should be very possible, its just that generating `defines.lua` requires a copy of the game installed, and it changes frequently between versions which might lead to breakage on different environment configurations

---
### Automatic migration between blueprint versions
Migration files are included in `factorio-data`, meaning that theoretically it might be possible to use their specification to convert old entity types into modern ones or vise-versa. 