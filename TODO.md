# TODO

### Add as many of the example programs to the test suite as possible
To help ensure that they're behaving correctly over any API changes, so they stay up-to-date

---
### Improve import organization
Move common constructs like `Vector` out of `draftsman.utils`, people shouldn't have to traverse all the way to `draftsman.classes.group` to import `Group`, etc.

---
### `EntityList.clear()` has some bad side effects, investigate and fix
Might make sense to actually move all of the spatial detection code into `EntityList`

---
### Add constraints on `DeconstructionPlanner`
General constraints on parameters and inputs; what you can deconstruct, what you can't, etc.

---
### Write `__repr__` function for everything
For most of the commonly-used things this is already the case, but would be nice if every Draftsman object had a nice, user-readable formatted output.

---
### Unify entity validation into one monolithic thing
Currently `Entity` and `Blueprintable` have two slightly different methods of converting their Python object representation to their output JSON dict/string format. Ideally this would be one single method (and thus one single point of failure to maintain).

---
### Write `dump_format` (and test_cases)
Do this not only for all the blueprintable types, but also each entity. In addition, include this output at the header of each documentation file, so people finally have a concrete reference for the actual blueprint string format
- Once that's done, maybe we can finally update the Factorio wiki to be up-to-date

---
### Python3-ify everything
Primarily this means changing all the type-comments to proper type-hints, as well as removing any 2.x compatibility code

Files done:
- [ ] `draftsman`
    - [ ] `classes`
        - [ ] `mixins`
        - [ ] `*`
    - [ ] `data`
    - [ ] `prototypes`
    - [ ] `*`
- [ ] `examples`
- [ ] `test`
    - [ ] `performance`
    - [ ] `prototypes`
    - [ ] `tools`
    - [ ] `*`

---
### Make draftsman's prototypes match Factorio's prototypes exactly (for consistency's sake)
As of writing there are a number of classes and class types that differ due to python functionality; it might make sense to unify the two so that class `AssemblingMachine` inherits the same classes in Factorio as it does in Draftsman.

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
### Maybe integrate defaults for more succinct blueprint strings?
A bootleg version of this currently exists already, where null entries are removed, but there should also be some kind of control for the "verbosity" of the output blueprint dict/string

---
### In the same vein as above, also perhaps an option for blueprint canonicalization
Ordering objects inside blueprints in regular ways for best compression, minimal git diff, etc.

---
### Investigate more performant alternatives to `schema` for format validation
- `validir`: peak performance (I think), but requires cython; currently we're pure python and wheel building would have to be set up. In addition, I'm not sure the feature set is complete enough for what I want
- `pydantic`: nicer, and we wouldn't have to build it ourselves; I'm currently investigating this one now. Unfortunately, it requires modern Python, which will make 2.0's minimum version greater than 1.0's
- Rolling our own: last resort; incredible amounts of work but features we can customize to our any need

---
### Add more examples
Should also probably subdivide the examples folder into subfolders like `rail`, `combinator`, `queries`, `misc`, etc.
And give each folder their own README.md that describes what each one does

---
### Investigate a Cython rewrite in efforts to make the library as performant as possible
Likely the last-most step, once all other feature requests and optimization passes are complete, to help squeeze as much out of the code-base as possible