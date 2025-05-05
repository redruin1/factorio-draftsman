# validatable.py

import attrs


@attrs.define(slots=False)
class Validatable:
    pass # TODO: define `validate_assignment` here and inherit