import pickle

from importlib.resources import files

from draftsman import data

try:
    source = files(data) / "equipment.pkl"
    with source.open("rb") as inp:
        _data = pickle.load(inp)
        grids: dict[str, dict] = _data[0]
        """
        Equipment grid definitions.

        :example:

        .. code-block:: python

            from draftsman.data import equipment
            print(equipment.grids["large-equipment-grid"])

        .. code-block:: python

            {
                'equipment_categories': ['armor'], 
                'type': 'equipment-grid', 
                'name': 'large-equipment-grid', 
                'width': 10, 
                'height': 10
            }

        :meta hide-value:
        """

except FileNotFoundError:  # pragma: no coverage
    grids: dict[str, dict] = {}
