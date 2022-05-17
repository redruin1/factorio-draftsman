# modules.py

from draftsman.data import entities, modules
from draftsman.warning import ModuleCapacityWarning

import warnings


class ModulesMixin(object):  # (RequestItemsMixin)
    """
    (Implicitly inherits :py:class:`~.RequestItemsMixin`)

    Allows the entity to have modules, and keep track of the amount of modules
    currently inside the entity.
    """

    def __init__(self, name, similar_entities, **kwargs):
        # type: (str, list[str], **dict) -> None

        # Get the total number of module slots
        try:
            self._total_module_slots = entities.raw[name]["module_specification"][
                "module_slots"
            ]
        except KeyError:
            self._total_module_slots = 0

        # Keep track of the current module slots currently used
        self._module_slots_occupied = 0

        super(ModulesMixin, self).__init__(name, similar_entities, **kwargs)

    # =========================================================================

    @property
    def total_module_slots(self):
        # type: () -> int
        """
        The total number of module slots in the Entity. Not exported; read only.

        :type: ``int``
        """
        return self._total_module_slots

    # =========================================================================

    @property
    def module_slots_occupied(self):
        # type: () -> int
        """
        The total number of module slots that are currently taken by inserted
        modules. Not exported; read only.

        :type: ``int``
        """
        return self._module_slots_occupied

    # =========================================================================

    def set_item_request(self, item, count):
        # type: (str, int) -> None
        new_count = count if count is not None else 0

        if item in modules.raw and new_count >= 0:
            self._module_slots_occupied -= self.items.get(item, 0)
            self._module_slots_occupied += new_count

        # Make sure we dont have too many modules in the Entity
        if self.module_slots_occupied > self.total_module_slots:
            warnings.warn(
                "Current number of module slots used ({}) greater than max "
                "module capacity ({})".format(
                    self.module_slots_occupied, self.total_module_slots
                ),
                ModuleCapacityWarning,
                stacklevel=2,
            )

        super(ModulesMixin, self).set_item_request(item, count)
