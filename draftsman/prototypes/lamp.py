# lamp.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
import draftsman.signatures as signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import lamps

import warnings


class Lamp(
    CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, Entity
):
    """ """

    def __init__(self, name=lamps[0], **kwargs):
        # type: (str, **dict) -> None
        super(Lamp, self).__init__(name, lamps, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def use_colors(self):
        # type: () -> bool
        """
        TODO
        """
        return self.control_behavior.get("use_colors", None)

    @use_colors.setter
    def use_colors(self, value):
        # type: (bool) -> None
        if value is None:
            self.control_behavior.pop("use_colors", None)
        elif isinstance(value, bool):
            self.control_behavior["use_colors"] = value
        else:
            raise TypeError("'use_colors' must be a bool or None")

    # def set_use_colors(self, value):
    #     # type: (bool) -> None
    #     """
    #     """
    #     if value is None:
    #         self.control_behavior.pop("use_colors", None)
    #     else:
    #         value = signatures.BOOLEAN.validate(value)
    #         self.control_behavior["use_colors"] = value
