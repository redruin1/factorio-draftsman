Versioning
==========

As of Draftsman 3.0, all import and export methods support loading from both Factorio 1.0 and Factorio 2.0 blueprint string formats:

.. doctest::

    >>> import json
    >>> from draftsman.entity import RocketSilo
    >>> silo = RocketSilo()
    >>> print(json.dumps(silo.to_dict(version=(1, 0), exclude_defaults=False), indent=4))
    {
        "name": "rocket-silo",
        "position": {
            "x": 4.5,
            "y": 4.5
        },
        "tags": {},
        "recipe": "rocket-part",
        "connections": {},
        "items": {},
        "auto_launch": false
    }
    >>> print(json.dumps(silo.to_dict(version=(2, 0), exclude_defaults=False), indent=4))
    {
        "name": "rocket-silo",
        "position": {
            "x": 4.5,
            "y": 4.5
        },
        "quality": "normal",
        "tags": {},
        "recipe": "rocket-part",
        "recipe_quality": "normal",
        "items": [],
        "control_behavior": {
            "read_items_mode": 1
        },
        "transitional_request_index": 0
    }


When importing blueprint strings, the version is automatically selected from the encoded :py:attr:`~Blueprint.version` value stored inside of the blueprint itself, so you don't have to manually specify a version.
However, if for some reason this value is incorrect, you can still pass a version to overwrite the encoded one with:

.. code-block:: python

    blueprint = Blueprint.from_string(bp_string, version=(2, 0)) # Make sure it's loaded as 2.0

