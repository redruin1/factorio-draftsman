# fluids.py

import pickle

from importlib.resources import files

from draftsman import data
from draftsman.error import InvalidFluidError

try:
    source = files(data) / "fluids.pkl"
    with source.open("rb") as inp:
        _data = pickle.load(inp)
        raw: dict[str, dict] = _data[0]
        """
        A dictionary where each key is the name of a known fluid and its value
        is it's ``data.raw`` prototype entry.

        :example:

        .. code-block:: python

            import json
            from draftsman.data import fluids
            print(fluids.raw["petroleum-gas"])

        .. code-block:: python

            {
                "subgroup": "fluid",
                "type": "fluid",
                "name": "petroleum-gas",
                "icon": "__base__/graphics/icons/fluid/petroleum-gas.png",
                "base_color": [
                    0.3,
                    0.1,
                    0.3
                ],
                "default_temperature": 25,
                "order": "a[fluid]-b[oil]-b[petroleum-gas]",
                "flow_color": [
                    0.8,
                    0.8,
                    0.8
                ]
            }

        :meta hide-value:
        """

except FileNotFoundError:  # pragma: no coverage
    raw: dict[str, dict] = {}


def add_fluid(name: str, order: str = None, **kwargs):
    """
    Add a new fluid, or modify the properties of an existing fluid. Useful for
    simulating a modded environment without having to fully supply an entire
    mod configuration for simple scripts.

    :param name: The name of the fluid to add.
    :param: The order string with which this fluid should be sorted with. If
        omitted, this fluid will be sorted by it's regular name lexographically.
    :param kwargs: Any additional values that a fluid prototype should have.
    """
    existing_data = raw.get(name, {})
    default_temperature = existing_data.get(
        "default_temperature", kwargs.get("default_temperature", 25)
    )
    raw[name] = {
        **existing_data,
        "type": "fluid",
        "name": name,
        "order": order if order is not None else "",
        "default_temperature": default_temperature,
        **kwargs,
    }
    # TODO: this should also update signals
    # TODO: what if the user sets auto-barrel to true in this function? Ideally
    # it would also generate barreling recipes and update them accordingly


def get_temperature_range(fluid_name: str) -> tuple[float, float]:
    """
    Gets a tuple representing the [minimum, maximum] temperature range for the
    fluid with name ``fluid_name``.

    :param fluid_name: The name of the fluid.

    :raises InvalidFluidError: if ``fluid_name`` is not a recognized fluid.

    :returns: A tuple of two floats, representing the minimum and maximum
        temperature this fluid can have, inclusive.
    """
    if fluid_name not in raw:
        raise InvalidFluidError("'{}'".format(fluid_name))

    # 'default_temperature' is required by FluidPrototype, and is equal to min
    min_temp = raw[fluid_name]["default_temperature"]

    # 'max_temperature' is optional, and defaults to 'default_temperature'
    max_temp = raw[fluid_name].get("max_temperature", min_temp)

    return (min_temp, max_temp)
