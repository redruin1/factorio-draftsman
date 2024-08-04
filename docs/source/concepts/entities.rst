# 1
blueprint.entities.validate_assignment = "strict" # I don't like the extra state implied here; this could be hidden as fuck if you don't know about it
blueprint.entities.append("unknown")

# vs

# 2
blueprint.entities.append("unknown", validate="strict") # not bad, but its another reserved keyword argument thats hard to distinguish from other entity members

# vs

# 3
blueprint.entities.append("unknown")
blueprint.entities.validate()
# Or
blueprint.entities[-1].validate() # if you just want to validate the last one added

# 3 is best: it mirrors the design pattern used on parent objects (permissive construction, then strict validation) and it allows for the most user flexibility in the most apparent way

# However how do we handle overlapping entities? Thats one of the few cases where issuing a warning from the actual append would be better than getting a report after the fact
# Hence, we should use a hybrid; you can use #2 for inplace validation (on by default perhaps) and #3 for when you want more control for when to validate

# Fuck, but how do we handle:
blueprint.entities[0] = {"name": "some-entity"}

blueprint.entities.append(...) # validates
blueprint.entities.insert(...) # validates
blueprint.entities = [...] # validates? perhaps it should depend on blueprint.validate_assignment
blueprint.entities[...] = ... # probably also makes sense to have it based on blueprint.validate_assignment

# Maybe validate_assignment is the answer, just not as a member of `EntityList`. When we construct a Blueprint, it's one of the arguments after all:

blueprint = Blueprint(validate_assignment="none")

blueprint.entities = [{"name": "some-entity"}] # raw value
blueprint.entities[-1] = {"name": "some-other-entity"} # raw value
blueprint.version = "wrong" # raw value

blueprint.validate_assignment = True

# Continue with conversion
# ...


# Remember: we need to convert things into "internal" format whenever possible. This means that we need to "construct" any provided entity regardless of whether we validate it or not!