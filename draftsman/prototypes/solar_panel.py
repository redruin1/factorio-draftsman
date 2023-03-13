# solar_panel.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.entity import Entity
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import solar_panels

import warnings


class SolarPanel(Entity):
    """
    An entity that produces electricity depending on the presence of the sun.
    """

    # fmt: off
    # _exports = {
    #     **Entity._exports
    # }
    # fmt: on

    _exports = {}
    _exports.update(Entity._exports)

    def __init__(self, name=solar_panels[0], **kwargs):
        # type: (str, **dict) -> None
        super(SolarPanel, self).__init__(name, solar_panels, **kwargs)

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )
