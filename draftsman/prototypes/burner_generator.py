# burner_generator.py

from draftsman.prototypes.mixins import DirectionalMixin, Entity
from draftsman.errors import InvalidEntityID
from draftsman.utils import warn_user

from draftsman.data.entities import burner_generators


class BurnerGenerator(DirectionalMixin, Entity):
    """
    TODO: think about, because burner generators from mods like Space 
    Exploration don't have orientation. Are they the same entity type?
    """
    def __init__(self, name: str = burner_generators[0], **kwargs):
        if name not in burner_generators:
            raise InvalidEntityID("'{}' is not a valid name for this type"
                                  .format(name))
        super(BurnerGenerator, self).__init__(name, **kwargs)

        for unused_arg in self.unused_args:
            warn_user("{} has no attribute '{}'".format(type(self), unused_arg))