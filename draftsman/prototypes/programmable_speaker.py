# programmable_speaker.py

from draftsman.prototypes.mixins import (
    CircuitConditionMixin, ControlBehaviorMixin, CircuitConnectableMixin, Entity
)
import draftsman.signatures as signatures
from draftsman.utils import signal_dict
from draftsman.warning import DraftsmanWarning, VolumeWarning

from draftsman.data.entities import programmable_speakers
import draftsman.data.entities as entities
import draftsman.data.instruments as instruments

from typing import Union
import warnings


class ProgrammableSpeaker(CircuitConditionMixin, ControlBehaviorMixin, 
                          CircuitConnectableMixin, Entity):
    """
    """
    def __init__(self, name = programmable_speakers[0], **kwargs):
        # type: (str, **dict) -> None
        super(ProgrammableSpeaker, self).__init__(
            name, programmable_speakers, **kwargs
        )

        # Name translations for all of the instruments and their notes
        self.instruments = instruments.instruments[self.name]
        #self.instruments = entities.raw[self.name]["instruments"]
        # Default instrument and note names
        self.instrument_id = 0
        self.note_id = 0

        self.parameters = {}
        if "parameters" in kwargs:
            self.set_parameters(kwargs["parameters"])
            self.unused_args.pop("parameters")
        self._add_export("parameters", lambda x: len(x) != 0)

        self.alert_parameters = {}
        if "alert_parameters" in kwargs:
            self.set_alert_parameters(kwargs["alert_parameters"])
            self.unused_args.pop("alert_parameters")
        self._add_export("alert_parameters", lambda x: len(x) != 0)

        if "control_behavior" in kwargs:
            self._normalize_circuit_parameters()

        for unused_arg in self.unused_args:
            warnings.warn(
                "{} has no attribute '{}'".format(type(self), unused_arg),
                DraftsmanWarning,
                stacklevel = 2
            )

    def set_parameters(self, parameters):
        # type: (dict) -> None
        """
        """
        self.parameters = signatures.PARAMETERS.validate(parameters)

    def set_alert_parameters(self, alert_parameters):
        # type: (dict) -> None
        """
        """
        self.alert_parameters = signatures.ALERT_PARAMETERS.validate(
            alert_parameters
        )

    def set_volume(self, volume):
        # type: (float) -> None
        """
        """
        if volume is None:
            self.parameters.pop("playback_volume", None)
        else:
            volume = signatures.FLOAT.validate(volume)
            if volume < 0.0 or volume > 1.0:
                warnings.warn(
                    "volume not in range of [0.0, 1.0], will be clamped "
                    "to this range on import",
                    VolumeWarning,
                    stacklevel=2
                )
            self.parameters["playback_volume"] = volume

    def set_global_playback(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.parameters.pop("playback_globally", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.parameters["playback_globally"] = value

    def set_show_alert(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.alert_parameters.pop("show_alert", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.alert_parameters["show_alert"] = value

    def set_polyphony(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.parameters.pop("allow_polyphony", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.parameters["allow_polyphony"] = value

    def set_show_alert_on_map(self, value):
        # type: (bool) -> None
        """
        """
        if value is None:
            self.alert_parameters.pop("show_on_map", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            self.alert_parameters["show_on_map"] = value

    def set_alert_icon(self, signal):
        # type: (str) -> None
        """
        """
        if signal is None:
            self.alert_parameters.pop("icon_signal_id", None)
        else:
            self.alert_parameters["icon_signal_id"] = signal_dict(signal)

    def set_alert_message(self, message):
        # type: (str) -> None
        """
        """
        if message is None:
            self.alert_parameters.pop("alert_message", None)
        else:
            message = signatures.STRING.validate(message)
            self.alert_parameters["alert_message"] = message

    def set_signal_value_is_pitch(self, value):
        # type: (bool) -> None
        """
        """
        # TODO: handle this with defaults
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_params = self.control_behavior["circuit_parameters"]

        if value is None:
            circuit_params.pop("signal_value_is_pitch", None)
            if len(circuit_params) == 0:
                self.control_behavior.pop("circuit_parameters", None)
        else:
            value = signatures.BOOLEAN.validate(value)
            circuit_params["signal_value_is_pitch"] = value

    def set_instrument(self, instrument):
        # type: (Union[int, str]) -> None
        """
        TODO: fix this function up, its an eyesore
        """

        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_params = self.control_behavior["circuit_parameters"]

        if instrument is None:
            circuit_params.pop("instrument_id", None)
            if len(circuit_params) == 0:
                self.control_behavior.pop("circuit_parameters", None)
        elif isinstance(instrument, int):
            # TODO: If index is out of range, issue Warning
            circuit_params["instrument_id"] = instrument
        elif isinstance(instrument, str):
            instrument = list(self.instruments).index(instrument)
            circuit_params["instrument_id"] = instrument
        else:
            raise TypeError("instrument_id is neither int nor str")


        # How I would like this function to be written:
        # if instrument is None:
        #     circuit_params.pop("instrument_id", None)
        #     self.instrument = 0
        # else:
        #     instrument = instruments.index[self.name][instrument]["self"]
        #     self.instrument = instrument
        #     circuit_params["instrument_id"] = instrument
        #     # raises keyerror if need be

    def set_note(self, note):
        # type: (int) -> None
        """
        TODO: fix this function up, its an eyesore
        """
        if "circuit_parameters" not in self.control_behavior:
            self.control_behavior["circuit_parameters"] = {}
        circuit_params = self.control_behavior["circuit_parameters"]

        if note is None:
            circuit_params.pop("note_id", None)
            if len(circuit_params) == 0:
                self.control_behavior.pop("circuit_parameters", None)
        elif isinstance(note, int):
            # TODO: If index is out of range, warn or error?
            circuit_params["note_id"] = note
        elif isinstance(note, str):
            # Look for instrument
            instrument_num = circuit_params.pop("instrument_id", None) or 0
            instrument_name = list(self.instruments)[instrument_num]
            # Get notes from that instrument
            instrument_notes = self.instruments[instrument_name]
            #print(instrument_notes)
            circuit_params["note_id"] = instrument_notes.index(note)
        else:
            raise TypeError("note_id is neither int nor str")

        # How I would like this function to be written:
        # if note is None:
        #     circuit_params.pop("note_id", None)
        # else:
        #     note = instruments.index[self.name][self.instrument][note]
        #     circuit_params["note_id"] = note
        #     # raises keyerror if need be

    def _normalize_circuit_parameters(self):
        """
        Ideally I would get rid of this function, but having access to the 
        entity's instrument seems necessary and I dont have access to that in
        draftsman.signatures
        """
        # TODO: handle strings using self.instruments
        if "circuit_parameters" in self.control_behavior:
            circuit_params = self.control_behavior["circuit_parameters"]
            # Set the instruments
            if "instrument_id" in circuit_params:
                instrument = circuit_params["instrument_id"]
                if isinstance(instrument, str):
                    instrument_id = list(self.instruments).index(instrument)
                    circuit_params["instrument_id"] = instrument_id
            
            if "note_id" in circuit_params:
                note = circuit_params["note_id"]
                if isinstance(note, str):
                    note_id = self.instruments[instrument].index(note)
                    circuit_params["note_id"] = note_id