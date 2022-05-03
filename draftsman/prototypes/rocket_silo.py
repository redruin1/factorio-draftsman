# rocket_silo.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import RequestItemsMixin
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import rocket_silos

import warnings


class RocketSilo(RequestItemsMixin, Entity):
    """
    An entity that produces rockets, usually used in research.
    """

    def __init__(self, name=rocket_silos[0], **kwargs):
        # type: (str, **dict) -> None
        super(RocketSilo, self).__init__(name, rocket_silos, **kwargs)

        self.auto_launch = None
        if "auto_launch" in kwargs:
            self.auto_launch = kwargs["auto_launch"]
            self.unused_args.pop("auto_launch")
        self._add_export("auto_launch", lambda x: x is not None)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def auto_launch(self):
        # type: () -> bool
        """
        Whether or not to automatically launch the rocket when it's cargo is
        full.

        :getter: Gets whether or not to automatically launch.
        :setter: Sets whether or not to automatically launch.
        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self._auto_launch

    @auto_launch.setter
    def auto_launch(self, value):
        # type: (bool) -> None
        if value is None or isinstance(value, bool):
            self._auto_launch = value
        else:
            raise TypeError("'auto_launch' must be a bool or None")
