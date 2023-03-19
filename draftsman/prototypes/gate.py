# gate.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import gates
from draftsman.data import entities

import warnings


class Gate(DirectionalMixin, Entity):
    """
    A wall that opens near the player.
    """

    # fmt: off
    _exports = {
        **Entity._exports,
        **DirectionalMixin._exports
    }
    # fmt: on

    def __init__(self, name=gates[0], **kwargs):
        # type: (str, **dict) -> None
        super(Gate, self).__init__(name, gates, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args
