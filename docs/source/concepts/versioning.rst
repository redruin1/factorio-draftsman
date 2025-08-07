Versioning
==========

As of Draftsman 3.0, all import and export methods support working with both Factorio 1.0 and Factorio 2.0 blueprint string formats:

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
        "items": {
            "productivity-module-3": 2
        },
        "tags": {},
        "direction": 0,
        "recipe": "rocket-part",
        "connections": {},
        "auto_launch": false
    }
    >>> print(json.dumps(silo.to_dict(version=(2, 0), exclude_defaults=False), indent=4))
    {
        "name": "rocket-silo",
        "position": {
            "x": 4.5,
            "y": 4.5
        },
        "mirror": false,
        "quality": "normal",
        "items": [
            {
                "id": {
                    "name": "productivity-module-3",
                    "quality": "normal"
                },
                "items": {
                    "in_inventory": [
                        {
                            "inventory": 4,
                            "stack": 0,
                            "count": 1
                        },
                        {
                            "inventory": 4,
                            "stack": 1,
                            "count": 1
                        }
                    ],
                    "grid_count": 0
                }
            }
        ],
        "tags": {},
        "direction": 0,
        "recipe": "rocket-part",
        "recipe_quality": "normal",
        "control_behavior": {
            "read_items_mode": 1
        },
        "use_transitional_requests": false,
        "transitional_request_index": 0
    }


When importing blueprint strings, the version is automatically selected from the encoded :py:attr:`~Blueprint.version` value stored inside of the blueprint itself, so you don't have to manually specify a version.
However, if for some reason this value is incorrect, you can still pass a version to overwrite the encoded one with:

.. code-block:: python

    blueprint = Blueprint.from_string(bp_string, version=(2, 0)) # Enforce that it's loaded as 2.0

In the case where no version is present in the input data, then Draftsman will default the the current environment's version - and if the environment is missing such information, to :py:data:`draftsman.DEFAULT_FACTORIO_VERSION`.
