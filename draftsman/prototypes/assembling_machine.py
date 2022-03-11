# assembling_machine.py

from draftsman.prototypes.mixins import RequestItemsMixin, RecipeMixin, Entity
from draftsman.warning import DraftsmanWarning, ModuleLimitationWarning

from draftsman.data.entities import assembling_machines
from draftsman.data import modules

import warnings


class AssemblingMachine(RecipeMixin, RequestItemsMixin, Entity):
    def __init__(self, name = assembling_machines[0], **kwargs):
        # type: (str, **dict) -> None
        super(AssemblingMachine, self).__init__(
            name, assembling_machines, **kwargs
        )

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_item_request(self, item, amount):
        # type: (str, int) -> None
        """
        Overwritten
        """
        # If the item is a module
        if item in modules.raw:
            # Check to make sure the recipe within the entity's limitations
            # (If it has any)
            module = modules.raw[item]
            if "limitation" in module:
                if self.recipe is not None and \
                   self.recipe not in module["limitation"]:
                    tooltip = module.get("limitation_message_key", None)
                    warnings.warn(
                        "cannot use module '{}' with recipe '{}' ({})"
                        .format(item, self.recipe, tooltip),
                        ModuleLimitationWarning,
                        stacklevel = 2
                    )
        
        super(AssemblingMachine, self).set_item_request(item, amount)