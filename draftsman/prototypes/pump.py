# pump.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
)
from draftsman.error import DataFormatError
from draftsman import signatures
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import pumps

from schema import SchemaError
import six
import warnings


class Pump(
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that aids fluid transfer through pipes.
    """

    # fmt: off
    _exports = {
        **Entity._exports,
        **DirectionalMixin._exports,
        **CircuitConnectableMixin._exports,
        **ControlBehaviorMixin._exports,
        **CircuitConditionMixin._exports,
    }
    # fmt: on

    _exports = {}
    _exports.update(Entity._exports)
    _exports.update(DirectionalMixin._exports)
    _exports.update(CircuitConnectableMixin._exports)
    _exports.update(ControlBehaviorMixin._exports)
    _exports.update(CircuitConditionMixin._exports)

    def __init__(self, name=pumps[0], **kwargs):
        # type: (str, **dict) -> None
        super(Pump, self).__init__(name, pumps, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

        del self.unused_args

    # =========================================================================

    __hash__ = Entity.__hash__

    @ControlBehaviorMixin.control_behavior.setter
    def control_behavior(self, value):
        # type: (dict) -> None
        try:
            self._control_behavior = signatures.PUMP_CONTROL_BEHAVIOR.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)
