# programmable_speaker.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    CircuitEnableMixin,
    EnergySourceMixin,
)
from draftsman.constants import ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    SignalID,
    uint32,
)
from draftsman.validators import conditional, instance_of, one_of
from draftsman.warning import (
    UnknownInstrumentWarning,
    UnknownNoteWarning,
    VolumeRangeWarning,
)

from draftsman.data.entities import programmable_speakers
import draftsman.data.instruments as instruments_data

import attrs
from typing import Literal, Optional
import warnings


@attrs.define
class ProgrammableSpeaker(
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    Entity,
):
    """
    An entity that makes sounds that can be controlled by circuit network
    signals.
    """

    @property
    def similar_entities(self) -> list[str]:
        return programmable_speakers

    # =========================================================================

    @property
    def instruments(self) -> dict[str, set]:
        """
        A dict of all instrument and note names that this ``ProgrammableSpeaker``
        has. Each key is the name of the instrument, and each value a ``set`` of
        string names of each note corresponding to that instrument. Not exported;
        read only.
        """
        result = {}
        for instrument in instruments_data.raw.get(self.name, {}):
            notes = set()
            for note in instrument["notes"]:
                notes.add(note["name"])
            result[instrument["name"]] = notes
        return result

    # =========================================================================

    signal_value_is_pitch: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not the value of the signal should indicate the particular note
    of the instrument to play. If this attribute is ``True``, then the signal
    that the speaker will read from is specified as the 
    :py:attr:`~Condition.first_signal` of 
    :py:attr:`~ProgrammableSpeaker.circuit_condition`.
    """

    # =========================================================================

    stop_playing_sounds: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not any change in the input playback signal will automatically
    cease the currently playing sound.
    """

    # =========================================================================

    volume_controlled_by_signal: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not the volume of this speaker should be dynamically controlled
    via circuit signal, or if it should always remain the constant value 
    specified by :py:attr:`.volume`.
    """

    # =========================================================================

    volume_signal: Optional[SignalID] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
    )
    """
    What volume signal to use when dynamically setting this speakers volume. Has
    no effect if :py:attr:`.volume_controlled_by_signal` is ``False``.
    """

    # =========================================================================

    volume: float = attrs.field(default=1.0, validator=instance_of(float))
    """
    The volume of the programmable speaker, in the range ``[0.0, 1.0]``.

    Raises :py:class:`VolumeRangeWarning` if set to a value outside of the
    range ``[0.0, 1.0]``.

    :exception DataFormatError: If set to anything other than a ``float``.
    """

    @volume.validator
    @conditional(ValidationMode.PEDANTIC)
    def _volume_validator(
        self,
        _: attrs.Attribute,
        value: float,
    ):
        if not (0.0 <= value <= 1.0):
            msg = "'volume' ({}) not in range [0.0, 1.0]; will be clamped to this range on import".format(
                value
            )
            warnings.warn(VolumeRangeWarning(msg))

    # =========================================================================

    playback_mode: Literal["local", "surface", "global"] = attrs.field(
        default="local", validator=one_of("local", "surface", "global")
    )
    """
    In what manner to broadcast the audio from this programmable speaker:

    * ``"local"`` only plays the audio when physically near the speaker, 
        attenuating volume based on distance.
    * ``"surface"`` plays the audio at a constant volume if the player is on the 
        same surface as the speaker.
    * ``"global"`` plays the audio at a constant volume across all surfaces.

    .. NOTE::

        In Factorio 1.0, only modes ``"local"`` and ``"surface"`` are permitted.

    :exception DataFormatError: If set to anything other than the values above.
    """

    # =========================================================================

    show_alert: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to show an alert to the player(s) if a sound is played.

    :exception DataFormatError: If set to anything other than a ``bool``.
    """

    # =========================================================================

    allow_polyphony: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not to allow the speaker to play multiple notes at once.

    :exception DataFormatError: If set to anything other than a ``bool``.
    """

    # =========================================================================

    show_alert_on_map: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to show the alert on the map where the speaker lives.

    :exception DataFormatError: If set to anything other than a ``bool``.
    """

    # =========================================================================

    alert_icon: Optional[SignalID] = attrs.field(
        default=None,
        converter=SignalID.converter,
        validator=instance_of(Optional[SignalID]),
        metadata={"never_null": True},
    )
    """
    What icon to show to the player(s) and on the map if the speaker makes a
    sound (and alerts are enabled).

    :exception IncompleteSignalError: If set to a ``str`` that is not a valid
        signal ID.
    :exception DataFormatError: If set to a ``dict`` that does not match
        :py:class:`.SIGNAL_ID`.
    """

    # =========================================================================

    alert_message: str = attrs.field(
        default="",
        converter=lambda v: "" if v is None else v,
        validator=instance_of(str),
    )
    """
    What message to show to the player(s) if the speaker makes a sound (and
    alerts are enabled).

    :exception DataFormatError: If set to anything other than a ``str`` or 
        ``None``.
    """

    # =========================================================================

    signal_value_is_pitch: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not the value of a signal determines the pitch of the note to
    play.

    :exception DataFormatError: If set to anything other than a ``bool``.
    """

    # =========================================================================

    instrument_id: Optional[uint32] = attrs.field(
        default=0,
        validator=instance_of(Optional[uint32]),
    )
    """
    Numeric index of the instrument, 0-indexed.

    :exception InvalidInstrumentID: If set to a number that is not
        recognized as a valid instrument index for this speaker.
    :exception DataFormatError: If set to anything other than an ``int`` or ``None``.
    """

    @instrument_id.validator
    @conditional(ValidationMode.STRICT)
    def _instrument_id_validator(
        self,
        _: attrs.Attribute,
        value: Optional[uint32],
    ):
        """
        Ensure that this ``instrument_id`` is valid for this entity.
        """
        # If we don't recognize entity.name, then we can't know that
        # the ID is invalid
        if self.name not in instruments_data.name_of:
            return value

        if value is not None and value not in instruments_data.name_of[self.name]:
            msg = "ID '{}' is not a known instrument for this programmable speaker".format(
                value
            )
            warnings.warn(UnknownInstrumentWarning(msg))

    # =========================================================================

    @property
    def instrument_name(self) -> Optional[str]:
        """
        Human readable name of the instrument. Returned based on the value of
        :py:attr:`.instrument_id`. Returns ``None`` if the instrument ID is not
        recognized, or if this programmable speaker is not recognized. Not
        exported.

        :getter: Gets the name of the current instrument, or ``None`` if not set.
        :setter: Sets the name of the current instrument. Removes the key if set
            to ``None``.

        :exception InvalidInstrumentID: If set to a name that is not recognized
            as a valid instrument index for this speaker.
        :exception DataFormatError: If set to anything other than a ``str`` or
            ``None``.
        """
        return (
            instruments_data.name_of.get(self.name, {})
            .get(self.instrument_id, {})
            .get("self", None)
        )

    @instrument_name.setter
    def instrument_name(self, value: Optional[str]):
        if value is None:
            self.instrument_id = None
        else:
            new_id = (
                instruments_data.index_of.get(self.name, {})
                .get(value, {})
                .get("self", None)
            )
            if new_id is None:
                msg = "Name '{}' is not a known instrument for this programmable speaker".format(
                    value
                )
                warnings.warn(UnknownInstrumentWarning(msg))
            self.instrument_id = new_id

    # =========================================================================

    note_id: Optional[uint32] = attrs.field(
        default=0, validator=instance_of(Optional[uint32])
    )
    """
    Numeric index of the note. Updated in tandem with ``note_name``.

    :exception InvalidInstrumentID: If set to a number that is not
        recognized as a valid note index for this speaker.
    :exception DataFormatError: If set to anything other than an ``int`` or 
        ``None``.
    """

    @note_id.validator
    @conditional(ValidationMode.STRICT)
    def _note_id_validator(
        self,
        _: attrs.Attribute,
        value: Optional[uint32],
    ):
        """
        Ensure that this ``note_id`` is valid for this entity.
        """
        # If we don't recognize entity.name or instrument_id, then
        # we can't know that the ID is invalid
        if self.name not in instruments_data.name_of:
            return
        if self.instrument_id not in instruments_data.name_of[self.name]:
            return

        if (
            value is not None
            and value not in instruments_data.name_of[self.name][self.instrument_id]
        ):
            msg = "ID '{}' is not a known note for this instrument and/or programmable speaker".format(
                value
            )
            warnings.warn(UnknownNoteWarning(msg))

    # =========================================================================

    @property
    def note_name(self) -> Optional[str]:
        """
        Name of the note. Derived from :py:attr:`.note_id`, but can be set via
        this attribute as well.

        :exception DataFormatError: If set to anything other than a ``str`` or
            ``None``.
        """
        return (
            instruments_data.name_of.get(self.name, {})
            .get(self.instrument_id, {})
            .get(self.note_id, None)
        )

    @note_name.setter
    def note_name(self, value: Optional[str]):
        if value is None:
            self.note_id = None
        else:
            new_id = (
                instruments_data.index_of.get(self.name, {})
                .get(self.instrument_name, {})
                .get(value, None)
            )
            if new_id is None:
                msg = "Name '{}' is not a known note for this instrument and/or programmable speaker".format(
                    value
                )
                warnings.warn(UnknownNoteWarning(msg))
            self.note_id = new_id

    # =========================================================================

    def merge(self, other: "ProgrammableSpeaker"):
        super().merge(other)

        # Control behavior
        self.signal_value_is_pitch = other.signal_value_is_pitch
        self.stop_playing_sounds = other.stop_playing_sounds
        self.instrument_id = other.instrument_id
        self.note_id = other.note_id
        # Parameters
        self.volume = other.volume
        self.playback_mode = other.playback_mode
        self.allow_polyphony = other.allow_polyphony
        self.volume_controlled_by_signal = other.volume_controlled_by_signal
        self.volume_signal = other.volume_signal
        # Alert Parameters
        self.show_alert = other.show_alert
        self.show_alert_on_map = other.show_alert_on_map
        self.alert_icon = other.alert_icon
        self.alert_message = other.alert_message

    # =========================================================================

    __hash__ = Entity.__hash__


@attrs.define
class _Export:
    playback_globally: bool = False


_export_fields = attrs.fields(_Export)


draftsman_converters.get_version((1, 0)).add_hook_fns(
    ProgrammableSpeaker,
    lambda fields: {
        (
            "control_behavior",
            "circuit_parameters",
            "signal_value_is_pitch",
        ): fields.signal_value_is_pitch.name,
        (
            "control_behavior",
            "circuit_parameters",
            "instrument_id",
        ): fields.instrument_id.name,
        ("control_behavior", "circuit_parameters", "note_id"): fields.note_id.name,
        ("parameters", "playback_volume"): fields.volume.name,
        ("parameters", "playback_globally"): (
            fields.playback_mode.name,
            lambda v, _: "surface" if v else "local",
        ),
        ("parameters", "allow_polyphony"): fields.allow_polyphony.name,
        ("alert_parameters", "show_alert"): fields.show_alert.name,
        ("alert_parameters", "show_on_map"): fields.show_alert_on_map.name,
        ("alert_parameters", "icon_signal_id"): fields.alert_icon.name,
        ("alert_parameters", "alert_message"): fields.alert_message.name,
    },
    lambda fields, _: {
        (
            "control_behavior",
            "circuit_parameters",
            "signal_value_is_pitch",
        ): fields.signal_value_is_pitch.name,
        (
            "control_behavior",
            "circuit_parameters",
            "instrument_id",
        ): fields.instrument_id.name,
        ("control_behavior", "circuit_parameters", "note_id"): fields.note_id.name,
        ("parameters", "playback_volume"): fields.volume.name,
        ("parameters", "playback_globally"): (
            _export_fields.playback_globally,
            lambda inst: True if inst.playback_mode == "surface" else False,
        ),
        ("parameters", "allow_polyphony"): fields.allow_polyphony.name,
        ("alert_parameters", "show_alert"): fields.show_alert.name,
        ("alert_parameters", "show_on_map"): fields.show_alert_on_map.name,
        ("alert_parameters", "icon_signal_id"): fields.alert_icon.name,
        ("alert_parameters", "alert_message"): fields.alert_message.name,
    },
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    ProgrammableSpeaker,
    lambda fields: {
        (
            "control_behavior",
            "circuit_parameters",
            "signal_value_is_pitch",
        ): fields.signal_value_is_pitch.name,
        (
            "control_behavior",
            "circuit_parameters",
            "stop_playing_sounds",
        ): fields.stop_playing_sounds.name,
        (
            "control_behavior",
            "circuit_parameters",
            "instrument_id",
        ): fields.instrument_id.name,
        ("control_behavior", "circuit_parameters", "note_id"): fields.note_id.name,
        ("parameters", "playback_volume"): fields.volume.name,
        ("parameters", "playback_mode"): fields.playback_mode.name,
        ("parameters", "allow_polyphony"): fields.allow_polyphony.name,
        (
            "parameters",
            "volume_controlled_by_signal",
        ): fields.volume_controlled_by_signal.name,
        ("parameters", "volume_signal_id"): fields.volume_signal.name,
        ("alert_parameters", "show_alert"): fields.show_alert.name,
        ("alert_parameters", "show_on_map"): fields.show_alert_on_map.name,
        ("alert_parameters", "icon_signal_id"): fields.alert_icon.name,
        ("alert_parameters", "alert_message"): fields.alert_message.name,
    },
)
