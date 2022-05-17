# programmable_speaker.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
)
from draftsman.error import (
    DataFormatError,
    DraftsmanError,
    InvalidInstrumentID,
    InvalidNoteID,
)
from draftsman.warning import DraftsmanWarning, VolumeRangeWarning

from draftsman.data.entities import programmable_speakers
import draftsman.data.instruments as instruments_data
from draftsman.data.signals import signal_dict

from schema import SchemaError
import six
from typing import Union
import warnings


class ProgrammableSpeaker(
    CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, Entity
):
    """
    An entity that makes sounds that can be controlled by circuit network
    signals.
    """

    def __init__(self, name=programmable_speakers[0], **kwargs):
        # type: (str, **dict) -> None
        super(ProgrammableSpeaker, self).__init__(name, programmable_speakers, **kwargs)

        # Name translations for all of the instruments and their notes
        self._instrument_ids = instruments_data.index[self.name]
        self._instrument_names = instruments_data.names[self.name]
        # self.instruments = entities.raw[self.name]["instruments"]
        self._instruments = {}
        # print(instruments_data.raw[self.name][0])
        for instrument in instruments_data.raw[self.name]:
            notes = set()
            for note in instrument["notes"]:
                notes.add(note["name"])
            self._instruments[instrument["name"]] = notes

        # Default instrument and note names
        # self.instrument_id = None
        # self.note_id = None

        # Set instrument_id (and instrument_name by association)
        try:
            self.instrument_id = self.control_behavior["circuit_parameters"][
                "instrument_id"
            ]
        except KeyError:
            self.instrument_id = None
        try:
            self.note_id = self.control_behavior["circuit_parameters"]["note_id"]
        except KeyError:
            self.note_id = None

        self.parameters = {}
        if "parameters" in kwargs:
            self.parameters = kwargs["parameters"]
            self.unused_args.pop("parameters")
        self._add_export("parameters", lambda x: x is not None and len(x) != 0)

        self.alert_parameters = {}
        if "alert_parameters" in kwargs:
            self.alert_parameters = kwargs["alert_parameters"]
            self.unused_args.pop("alert_parameters")
        self._add_export("alert_parameters", lambda x: x is not None and len(x) != 0)

        # if "control_behavior" in kwargs:
        #     self._normalize_circuit_parameters()

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel=2,
            )

    # =========================================================================

    @property
    def instruments(self):
        # type: () -> dict
        """
        A list of all instruments that this ``ProgrammableSpeaker`` has. Not
        exported; read only.

        :type: ``list``.
        """
        return self._instruments

    # =========================================================================

    @property
    def parameters(self):
        # type: () -> dict
        """
        A set of general attributes that affect this programmable speaker.

        :getter: Gets the parameters of the speaker.
        :setter: Sets the parameters of the speaker.
        :type: :py:class:`.PARAMETERS`

        :exception DataFormatError: If set to anything that does not match the
            :py:class:`.PARAMETERS` format.
        """
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        # type: (dict) -> None
        try:
            self._parameters = signatures.PARAMETERS.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def alert_parameters(self):
        # type: () -> dict
        """
        A set of attributes that affect the alert this programmable speaker
        makes (if it's set to do so).

        :getter: Gets the alert parameters of the speaker.
        :setter: Sets the alert parameters of the speaker.
        :type: :py:class:`.ALERT_PARAMETERS`

        :exception DataFormatError: If set to anything that does not match the
            :py:class:`.ALERT_PARAMETERS` format.
        """
        return self._alert_parameters

    @alert_parameters.setter
    def alert_parameters(self, value):
        # type: (dict) -> None
        try:
            self._alert_parameters = signatures.ALERT_PARAMETERS.validate(value)
        except SchemaError as e:
            six.raise_from(DataFormatError(e), None)

    # =========================================================================

    @property
    def volume(self):
        # type: () -> float
        """
        The volume of the programmable speaker, in the range ``[0.0, 1.0]``.

        Raises :py:class:`VolumeRangeWarning` if set to a value outside of the
        range ``[0.0, 1.0]``.

        :getter: Gets the volume of the speaker, or ``None`` if not set.
        :setter: Sets the volume of the speaker. Removes the key if set to
            ``None``.
        :type: ``float``

        :exception TypeError: If set to anything other than a ``float`` or
            ``None``.
        """
        return self.parameters.get("playback_volume", None)

    @volume.setter
    def volume(self, value):
        # type: (float) -> None
        if value is None:
            self.parameters.pop("playback_volume", None)
        elif isinstance(value, float):
            if not 0.0 <= value <= 1.0:
                warnings.warn(
                    "volume ({}) not in range of [0.0, 1.0], will be clamped "
                    "on import".format(value),
                    VolumeRangeWarning,
                    stacklevel=2,
                )
            self.parameters["playback_volume"] = value
        else:
            raise TypeError("'volume' must be a float or None")

    # =========================================================================

    @property
    def global_playback(self):
        # type: () -> bool
        """
        Whether or not to play this sound at a constant volume regardless of
        distance.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.parameters.get("playback_globally", None)

    @global_playback.setter
    def global_playback(self, value):
        # type: (bool) -> None
        if value is None:
            self.parameters.pop("playback_globally", None)
        elif isinstance(value, bool):
            self.parameters["playback_globally"] = value
        else:
            raise TypeError("'global_playback' must be a bool or None")

    # =========================================================================

    @property
    def show_alert(self):
        # type: () -> bool
        """
        Whether or not to show an alert to the player(s) if a sound is played.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.alert_parameters.get("show_alert", None)

    @show_alert.setter
    def show_alert(self, value):
        # type: (bool) -> None
        if value is None:
            self.alert_parameters.pop("show_alert", None)
        elif isinstance(value, bool):
            self.alert_parameters["show_alert"] = value
        else:
            raise TypeError("'show_alert' must be a bool or None")

    # =========================================================================

    @property
    def allow_polyphony(self):
        # type: () -> bool
        """
        Whether or not to allow the speaker to play multiple notes at once.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.parameters.get("allow_polyphony", None)

    @allow_polyphony.setter
    def allow_polyphony(self, value):
        # type: (bool) -> None
        if value is None:
            self.parameters.pop("allow_polyphony", None)
        elif isinstance(value, bool):
            self.parameters["allow_polyphony"] = value
        else:
            raise TypeError("'allow_polyphony' must be a bool or None")

    # =========================================================================

    @property
    def show_alert_on_map(self):
        # type: () -> bool
        """
        Whether or not to show the alert on the map where the speaker lives.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.alert_parameters.get("show_on_map", None)

    @show_alert_on_map.setter
    def show_alert_on_map(self, value):
        # type: (bool) -> None
        if value is None:
            self.alert_parameters.pop("show_on_map", None)
        elif isinstance(value, bool):
            self.alert_parameters["show_on_map"] = value
        else:
            raise TypeError("'show_on_map' must be a bool or None")

    # =========================================================================

    @property
    def alert_icon(self):
        # type: () -> dict
        """
        What icon to show to the player(s) and on the map if the speaker makes a
        sound (and alerts are enabled).

        :type: :py:class:`.SIGNAL_ID`

        :exception InvalidSignalError: If set to a ``str`` that is not a valid
            signal ID.
        :exception DataFormatError: If set to a ``dict`` that does not match
            :py:class:`.SIGNAL_ID`.
        """
        return self.alert_parameters.get("icon_signal_id", None)

    @alert_icon.setter
    def alert_icon(self, value):
        # type: (Union[str, dict]) -> None
        if value is None:
            self.alert_parameters.pop("icon_signal_id", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            self.alert_parameters["icon_signal_id"] = signal_dict(value)
        else:  # dict or other
            try:
                value = signatures.SIGNAL_ID.validate(value)
                self.alert_parameters["icon_signal_id"] = value
            except SchemaError:
                raise TypeError("Incorrectly formatted SignalID")

    # =========================================================================

    @property
    def alert_message(self):
        # type: () -> str
        """
        What message to show to the player(s) if the speaker makes a sound (and
        alerts are enabled).

        :type: :py:class:`.SIGNAL_ID`

        :exception InvalidSignalError: If set to a ``str`` that is not a valid
            signal ID.
        :exception DataFormatError: If set to a ``dict`` that does not match
            :py:class:`.SIGNAL_ID`.
        """
        return self.alert_parameters.get("alert_message", None)

    @alert_message.setter
    def alert_message(self, value):
        # type: (str) -> None
        if value is None:
            self.alert_parameters.pop("alert_message", None)
        elif isinstance(value, six.string_types):
            self.alert_parameters["alert_message"] = six.text_type(value)
        else:
            raise TypeError("'alert_message' must be a str or None")

    # =========================================================================

    @property
    def signal_value_is_pitch(self):
        # type: () -> bool
        """
        Whether or not the value of a signal determines the pitch of the note to
        play.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        if "circuit_parameters" not in self.control_behavior:
            return None
        circuit_parameters = self.control_behavior["circuit_parameters"]

        return circuit_parameters.get("signal_value_is_pitch", None)

    @signal_value_is_pitch.setter
    def signal_value_is_pitch(self, value):
        # type: (bool) -> None
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_parameters = self.control_behavior["circuit_parameters"]

        if value is None:
            circuit_parameters.pop("signal_value_is_pitch", None)
            if len(circuit_parameters) == 0:
                self.control_behavior.pop("circuit_parameters", None)
        elif isinstance(value, bool):
            circuit_parameters["signal_value_is_pitch"] = value
        else:
            raise TypeError("'signal_value_is_pitch' must be a bool or None")

    # =========================================================================

    @property
    def instrument_id(self):
        # type: () -> int
        """
        Numeric index of the instrument. Updated in tandem with
        ``instrument_name``.

        :getter: Gets the number of the current instrument, or ``None`` if not
            set.
        :setter: Sets the number of the current instrument. Removes the key if
            set to ``None``.

        :exception InvalidInstrumentID: If set to a number that is not
            recognized as a valid instrument index for this speaker.
        :exception TypeError: If set to anything other than an ``int`` or ``None``.
        """
        if "circuit_parameters" not in self.control_behavior:
            return None
        circuit_parameters = self.control_behavior["circuit_parameters"]

        return circuit_parameters.get("instrument_id", None)

    @instrument_id.setter
    def instrument_id(self, value):
        # type: (int) -> None
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_parameters = self.control_behavior["circuit_parameters"]

        if value is None:
            circuit_parameters.pop("instrument_id", None)
            self._instrument_name = None
            circuit_parameters.pop("note_id", None)
            self._note_name = None
            if len(circuit_parameters) == 0:
                self.control_behavior.pop("circuit_parameters", None)
        elif isinstance(value, int):
            if value not in self._instrument_names:
                raise InvalidInstrumentID("'{}'".format(value))

            # Remove the note if the instrument changed
            if circuit_parameters.get("instrument_id", None) != value:
                circuit_parameters.pop("note_id", None)
                self._note_name = None

            circuit_parameters["instrument_id"] = value
            self._instrument_name = self._instrument_names[value]["self"]
        else:
            raise TypeError("'instrument_id' must be an int or None")

    # =========================================================================

    @property
    def instrument_name(self):
        # type: () -> str
        """
        Name of the instrument. Updated in tandem with ``instrument_id``. Not
        exported.

        :getter: Gets the name of the current instrument, or ``None`` if not set.
        :setter: Sets the name of the current instrument. Removes the key if set
            to ``None``.

        :exception InvalidInstrumentID: If set to a name that is not recognized
            as a valid instrument index for this speaker.
        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        """
        return self._instrument_name

    @instrument_name.setter
    def instrument_name(self, value):
        # type: (str) -> None
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_parameters = self.control_behavior["circuit_parameters"]

        if value is None:
            circuit_parameters.pop("instrument_id", None)
            self._instrument_name = None
            circuit_parameters.pop("note_id", None)
            self._note_name = None
            if len(circuit_parameters) == 0:
                self.control_behavior.pop("circuit_parameters", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            if value not in self._instrument_ids:
                raise InvalidInstrumentID("'{}'".format(value))

            # Remove the note if the instrument changed
            if hasattr(self, "_instrument_name") and self._instrument_name != value:
                circuit_parameters.pop("note_id", None)
                self._note_name = None

            self._instrument_name = value
            circuit_parameters["instrument_id"] = self._instrument_ids[value]["self"]
        else:
            raise TypeError("'instrument_name' must be a str or None")

    # =========================================================================

    @property
    def note_id(self):
        # type: () -> int
        """
        Numeric index of the note. Updated in tandem with ``note_name``.

        :getter: Gets the number of the current note, or ``None`` if not set.
        :setter: Sets the number of the current note. Removes the key if set to
            ``None``.

        :exception InvalidInstrumentID: If set to a number that is not
            recognized as a valid note index for this speaker.
        :exception TypeError: If set to anything other than an ``int`` or ``None``.
        """
        if "circuit_parameters" not in self.control_behavior:
            return None
        circuit_parameters = self.control_behavior["circuit_parameters"]

        return circuit_parameters.get("note_id", None)

    @note_id.setter
    def note_id(self, value):
        # type: (int) -> None
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_parameters = self.control_behavior["circuit_parameters"]

        if value is None:
            circuit_parameters.pop("note_id", None)
            self._note_name = None
            if len(circuit_parameters) == 0:
                self.control_behavior.pop("circuit_parameters", None)
        elif isinstance(value, int):
            if "instrument_id" not in circuit_parameters:
                raise DraftsmanError("Cannot set note before setting instrument")
            instrument_id = circuit_parameters["instrument_id"]

            if value not in self._instrument_names[instrument_id]:
                raise InvalidNoteID("'{}'".format(value))

            circuit_parameters["note_id"] = value
            self._note_name = self._instrument_names[instrument_id][value]
        else:
            raise TypeError("'note_id' must be an int or None")

    # =========================================================================

    @property
    def note_name(self):
        # type: () -> str
        """
        Name of the note. Updated in tandem with ``note_id``. Not exported.

        :getter: Gets the name of the current instrument, or ``None`` if not set.
        :setter: Sets the name of the current instrument. Removes the key if set
            to ``None``.

        :exception InvalidInstrumentID: If set to a name that is not recognized
            as a valid instrument name for this speaker.
        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        """
        return self._note_name

    @note_name.setter
    def note_name(self, value):
        # type: (str) -> None
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_parameters = self.control_behavior["circuit_parameters"]

        if value is None:
            circuit_parameters.pop("note_id", None)
            self._note_name = None
            if len(circuit_parameters) == 0:
                self.control_behavior.pop("circuit_parameters", None)
        elif isinstance(value, six.string_types):
            value = six.text_type(value)
            if "instrument_id" not in circuit_parameters:
                raise DraftsmanError("Cannot set note before setting instrument")
            instrument_name = self._instrument_name

            if value not in self._instrument_ids[instrument_name]:
                raise InvalidNoteID("'{}'".format(value))

            self._note_name = value
            circuit_parameters["note_id"] = self._instrument_ids[instrument_name][value]
        else:
            raise TypeError("'note_name' must be a str or None")

    # =========================================================================

    def _normalize_circuit_parameters(self):
        """
        Ideally I would get rid of this function, but having access to the
        entity's instrument seems necessary and I dont have access to that in
        draftsman.signatures
        """
        # if "circuit_parameters" in self.control_behavior:
        #     circuit_params = self.control_behavior["circuit_parameters"]
        #     # Set the instruments
        #     if "instrument_id" in circuit_params:
        #         instrument = circuit_params["instrument_id"]
        #         if isinstance(instrument, str):
        #             instrument_id = list(self.instruments).index(instrument)
        #             circuit_params["instrument_id"] = instrument_id

        #     if "note_id" in circuit_params:
        #         note = circuit_params["note_id"]
        #         if isinstance(note, str):
        #             note_id = self.instruments[instrument].index(note)
        #             circuit_params["note_id"] = note_id
