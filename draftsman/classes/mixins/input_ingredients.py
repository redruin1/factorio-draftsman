# input_ingredients.py


class InputIngredientsMixin:
    @property
    def ingredient_items(self):
        """
        The subset of :py:attr:`.items` where each key is a valid input
        ingredient that can be consumed by this entity. Returns an empty dict if
        this entity consumes no ingredients, or what ingredients this entity
        consumes cannot be deduced with the current data configuration.
        """
        return [
            item_request
            for item_request in self.item_requests
            if item_request.id.name in self.allowed_input_ingredients
        ]
