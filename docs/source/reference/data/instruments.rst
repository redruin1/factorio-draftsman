.. py:currentmodule:: draftsman.data.instruments

:py:mod:`~draftsman.data.instruments`
=====================================

.. py:data:: raw

    A ``dict`` of all instruments indexed by the name of the speaker that plays them.

    .. seealso::

        `<https://wiki.factorio.com/Prototype/ProgrammableSpeaker#instruments>`_

    .. code-block:: python

        import json
        from draftsman.data import instruments

        print(json.dumps(instruments.raw["programmable-speaker"], indent=4))

    .. code-block:: text

        [
            {
                "name": "alarms",
                "notes": [
                    {
                        "name": "alarm-1",
                        "sound": {
                            "filename": "__base__/sound/programmable-speaker/alarm-1.ogg"
                        }
                    },
                    {
                        "name": "alarm-2",
                        "sound": {
                            "filename": "__base__/sound/programmable-speaker/alarm-2.ogg"
                        }
                    },
                    {
                        "name": "buzzer-1",
                        "sound": {
                            "filename": "__base__/sound/programmable-speaker/buzzer-1.ogg"
                        }
                    },
                    {
                        "name": "buzzer-2",
                        "sound": {
                            "filename": "__base__/sound/programmable-speaker/buzzer-2.ogg"
                        }
                    },
                    {
                        "name": "buzzer-3",
                        "sound": {
                            "filename": "__base__/sound/programmable-speaker/buzzer-3.ogg"
                        }
                    },
                    {
                        "name": "ring",
                        "sound": {
                            "preload": false,
                            "filename": "__base__/sound/programmable-speaker/ring.ogg"
                        }
                    },
                    {
                        "name": "siren",
                        "sound": {
                            "preload": false,
                            "filename": "__base__/sound/programmable-speaker/siren.ogg"
                        }
                    }
                ]
            },
            # ...
        ]

.. py:data:: index

    A quick reference dict that provides the numeric equivalent to a key index.
    The inverse of :py:data:`names`.
    Follows the format:

    .. code-block:: python

        {
            "programmable_speaker_name": {
                "instrument_name_1": {
                    "self": 0 # This is the index of the instrument
                    "note_1": 0,
                    "note_2": 1,
                    # ...
                },
                "instrument_name_2": {
                    # ...
                }
                # ...
            }
        }

    :example:

    .. code-block:: python

        import json
        from draftsman.data import instruments

        print(json.dumps(instruments.index["programmable-speaker"]["drum-kit"], indent=4))

    .. code-block:: text

        {
            "self": 2,
            "kick-1": 0,
            "kick-2": 1,
            "snare-1": 2,
            "snare-2": 3,
            "snare-3": 4,
            "hat-1": 5,
            "hat-2": 6,
            "fx": 7,
            "high-q": 8,
            "perc-1": 9,
            "perc-2": 10,
            "crash": 11,
            "reverse-cymbal": 12,
            "clap": 13,
            "shaker": 14,
            "cowbell": 15,
            "triangle": 16
        }

.. py:data:: names

    A quick reference dict that provides the key equivalent to a numeric index.
    The inverse of :py:data:`index`.
    Follows the format:

    .. code-block:: python

        {
            "programmable_speaker_name": {
                0: {
                    "self": "instrument_name_1"
                    0: "note_1",
                    1: "note_2",
                    # ...
                },
                1: {
                    # ...
                }
                # ...
            }
        }

    :example:

    .. code-block:: python

        import json
        from draftsman.data import instruments

        print(json.dumps(instruments.names["programmable-speaker"][2], indent=4))

    .. code-block:: text

        {
            "self": "drum-kit",
            0: "kick-1",
            1: "kick-2",
            2: "snare-1",
            3: "snare-2",
            4: "snare-3",
            5: "hat-1",
            6: "hat-2",
            7: "fx",
            8: "high-q",
            9: "perc-1",
            10: "perc-2",
            11: "crash",
            12: "reverse-cymbal",
            13: "clap",
            14: "shaker",
            15: "cowbell",
            16: "triangle"
        }