# programmable_speaker.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    CircuitConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnableDisableMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import Connections, DraftsmanBaseModel, SignalID, uint32
from draftsman.utils import get_first
from draftsman.warning import (
    UnknownInstrumentWarning,
    UnknownNoteWarning,
    VolumeRangeWarning,
)

from draftsman.data.entities import programmable_speakers
import draftsman.data.instruments as instruments_data

from pydantic import (
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
)
from typing import Any, Literal, Optional, Union


class ProgrammableSpeaker(
    CircuitConditionMixin,
    EnableDisableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    Entity,
):
    """
    An entity that makes sounds that can be controlled by circuit network
    signals.
    """

    class Format(
        CircuitConditionMixin.Format,
        EnableDisableMixin.Format,
        ControlBehaviorMixin.Format,
        CircuitConnectableMixin.Format,
        Entity.Format,
    ):
        class ControlBehavior(
            CircuitConditionMixin.ControlFormat,
            EnableDisableMixin.ControlFormat,
            DraftsmanBaseModel,
        ):
            class CircuitParameters(DraftsmanBaseModel):
                signal_value_is_pitch: Optional[bool] = Field(
                    False,
                    description="""
                    Whether or not to use the value of the input signal to 
                    index the note in the selected instrument category. A input
                    signal value of '1' plays the first note, '2' the second,
                    etc. For the traditional instruments, this results in the
                    effect that higher input values will result in higher pitch
                    notes emitted from the speaker.
                    """,
                )
                instrument_id: Optional[uint32] = Field(
                    0,
                    description="""
                    The index of the instrument in the available instruments, 
                    0-based.
                    """,
                )
                instrument_name: Optional[str] = Field(
                    None,
                    exclude=True,
                    description="""
                    The human-readable name of this instrument; Not exported.
                    """,
                )
                note_id: Optional[uint32] = Field(
                    0,
                    description="""
                    The index of the note in the currently selected instrument's
                    notes, 0-based.
                    """,
                )
                note_name: Optional[str] = Field(
                    None,
                    exclude=True,
                    description="""
                    The human-readable name of this note; Not exported.
                    """,
                )

                @field_validator("instrument_id")
                @classmethod
                def ensure_instrument_id_known(
                    cls, value: Optional[int], info: ValidationInfo
                ):
                    if not info.context:
                        return value
                    if info.context["mode"] <= ValidationMode.MINIMUM:
                        return value

                    entity: "ProgrammableSpeaker" = info.context["object"]
                    warning_list: list = info.context["warning_list"]

                    # If we don't recognize entity.name, then we can't know that
                    # the ID is invalid
                    if entity.name not in instruments_data.name_of:
                        return value

                    if (
                        value is not None
                        and value not in instruments_data.name_of[entity.name]
                    ):
                        warning_list.append(
                            UnknownInstrumentWarning(
                                "ID '{}' is not a known instrument for this programmable speaker".format(
                                    value
                                )
                            )
                        )

                    return value

                @field_validator("instrument_name")
                @classmethod
                def ensure_instrument_name_known(
                    cls, value: Optional[str], info: ValidationInfo
                ):
                    if not info.context:
                        return value
                    if info.context["mode"] <= ValidationMode.MINIMUM:
                        return value

                    entity: "ProgrammableSpeaker" = info.context["object"]
                    warning_list: list = info.context["warning_list"]

                    # If we don't recognize entity.name, then we can't know that
                    # the ID is invalid
                    if entity.name not in instruments_data.index_of:
                        return value

                    if (
                        value is not None
                        and value not in instruments_data.index_of[entity.name]
                    ):
                        warning_list.append(
                            UnknownInstrumentWarning(
                                "Name '{}' is not a known instrument for this programmable speaker".format(
                                    value
                                )
                            )
                        )

                    return value

                @field_validator("note_id")
                @classmethod
                def ensure_note_id_known(
                    cls, value: Optional[int], info: ValidationInfo
                ):
                    if not info.context:
                        return value
                    if info.context["mode"] <= ValidationMode.MINIMUM:
                        return value

                    entity: "ProgrammableSpeaker" = info.context["object"]
                    warning_list: list = info.context["warning_list"]

                    # If we don't recognize entity.name or instrument_id, then
                    # we can't know that the ID is invalid
                    if entity.name not in instruments_data.name_of:
                        return value
                    if (
                        entity.instrument_id
                        not in instruments_data.name_of[entity.name]
                    ):
                        return value

                    if (
                        value is not None
                        and value
                        not in instruments_data.name_of[entity.name][
                            entity.instrument_id
                        ]
                    ):
                        warning_list.append(
                            UnknownNoteWarning(
                                "ID '{}' is not a known note for this instrument and/or programmable speaker".format(
                                    value
                                )
                            )
                        )

                    return value

                @field_validator("note_name")
                @classmethod
                def ensure_note_name_known(
                    cls, value: Optional[int], info: ValidationInfo
                ):
                    if not info.context:
                        return value
                    if info.context["mode"] <= ValidationMode.MINIMUM:
                        return value

                    entity: "ProgrammableSpeaker" = info.context["object"]
                    warning_list: list = info.context["warning_list"]

                    # If we don't recognize entity.name or instrument_id, then
                    # we can't know that the ID is invalid
                    if entity.name not in instruments_data.index_of:
                        return value
                    if (
                        entity.instrument_name
                        not in instruments_data.index_of[entity.name]
                    ):
                        return value

                    if (
                        value is not None
                        and value
                        not in instruments_data.index_of[entity.name][
                            entity.instrument_name
                        ]
                    ):
                        warning_list.append(
                            UnknownNoteWarning(
                                "Name '{}' is not a known note for this instrument and/or programmable speaker".format(
                                    value
                                )
                            )
                        )

                    return value

            circuit_parameters: Optional[CircuitParameters] = CircuitParameters()

        control_behavior: Optional[ControlBehavior] = ControlBehavior()

        class Parameters(DraftsmanBaseModel):
            playback_volume: Optional[float] = Field(
                1.0,
                description="""
                The volume with which to broadcast all sounds emitted by this
                programmable speaker, in the range [0.0, 1.0]. Values outside of
                this range are clipped to it.
                """,
            )
            playback_globally: Optional[bool] = Field(
                False,
                description="""
                Whether or not to have the programmable speaker distribute it's
                sound evenly across the entire surface, or only locally to the
                area it's placed.
                """,
            )
            allow_polyphony: Optional[bool] = Field(
                False,
                description="""
                Allows up to 10 sounds to be played at the same time, allowing
                for layering sounds. When false, notes will wait until their
                entire sound has played before repeating.
                """,
            )

            @field_validator("playback_volume")
            @classmethod
            def volume_in_range(cls, value: Optional[float], info: ValidationInfo):
                if not info.context:
                    return value
                if info.context["mode"] is ValidationMode.MINIMUM:
                    return value

                warning_list: list = info.context["warning_list"]
                if value is not None and not 0.0 <= value <= 1.0:
                    issue = VolumeRangeWarning(
                        "'playback_volume' ({}) not in range [0.0, 1.0]".format(value)
                    )

                    if info.context["mode"] is ValidationMode.PEDANTIC:
                        raise ValueError(issue) from None
                    else:
                        warning_list.append(issue)

                return value

        parameters: Optional[Parameters] = Parameters()

        class AlertParameters(DraftsmanBaseModel):
            show_alert: Optional[bool] = Field(
                False,
                description="""
                Whether or not to show any kind of alert when this speaker is
                in operation. At minimum, enabling this feature will generate an
                alert icon in the bottom right corner which will direct the 
                player to the programmable speaker.
                """,
            )
            show_on_map: Optional[bool] = Field(
                True,
                description="""
                Whether or not to show the 'icon_signal_id' icon as a flashing
                icon on the map surface, if 'show_alert' is true.
                """,
            )
            icon_signal_id: Optional[SignalID] = Field(
                None,
                description="""
                The signal icon image to broadcast the alert as, if 'show_alert'
                is true. This is used both for the alert in the bottom right 
                corner as well as the map view icon, if applicable.
                """,
            )
            alert_message: Optional[str] = Field(
                None,
                description="""
                A custom message to distribute alongside an alert, if 
                'show_alert' is true. If no message is provided the alert will
                simply point to the speakers location on the map.
                """,
            )

        alert_parameters: Optional[AlertParameters] = AlertParameters()

        model_config = ConfigDict(title="ProgrammableSpeaker")

    def __init__(
        self,
        name: Optional[str] = get_first(programmable_speakers),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        connections: Connections = {},
        control_behavior: Format.ControlBehavior = {},
        parameters: Format.Parameters = {},
        alert_parameters: Format.AlertParameters = {},
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """
        self._root: __class__.Format
        self.control_behavior: __class__.Format.ControlBehavior

        super().__init__(
            name,
            programmable_speakers,
            position=position,
            tile_position=tile_position,
            connections=connections,
            control_behavior=control_behavior,
            tags=tags,
            **kwargs
        )

        # TODO: cache this in a module variable so no redundant data
        self._instruments = {}
        # print(instruments_data.raw[self.name][0])
        for instrument in instruments_data.raw.get(self.name, {}):
            notes = set()
            for note in instrument["notes"]:
                notes.add(note["name"])
            self._instruments[instrument["name"]] = notes

        self.parameters = parameters
        self.alert_parameters = alert_parameters

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    @property
    def instruments(self) -> dict[str, set]:
        """
        A dict of all instrument and note names that this ``ProgrammableSpeaker``
        has. Each key is the name of the instrument, and each value a ``set`` of
        string names of each note corresponding to that instrument. Not exported;
        read only.

        :type: ``dict[str, set]``.
        """
        return self._instruments

    # =========================================================================

    @property
    def parameters(self) -> Optional[Format.Parameters]:
        """
        A set of general attributes that affect this programmable speaker.

        :getter: Gets the parameters of the speaker.
        :setter: Sets the parameters of the speaker.
        :type: :py:class:`.PARAMETERS`

        :exception DataFormatError: If set to anything that does not match the
            :py:class:`.PARAMETERS` format.
        """
        return self._root.parameters

    @parameters.setter
    def parameters(self, value: Optional[Format.Parameters]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "parameters", value
            )
            self._root.parameters = result
        else:
            self._root.parameters = value

    # =========================================================================

    @property
    def alert_parameters(self) -> Optional[Format.AlertParameters]:
        """
        A set of attributes that affect the alert this programmable speaker
        makes (if it's set to do so).

        :getter: Gets the alert parameters of the speaker.
        :setter: Sets the alert parameters of the speaker.
        :type: :py:class:`.ALERT_PARAMETERS`

        :exception DataFormatError: If set to anything that does not match the
            :py:class:`.ALERT_PARAMETERS` format.
        """
        return self._root.alert_parameters

    @alert_parameters.setter
    def alert_parameters(self, value: Optional[Format.AlertParameters]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self, type(self).Format, self._root, "alert_parameters", value
            )
            self._root.alert_parameters = result
        else:
            self._root.alert_parameters = value

    # =========================================================================

    @property
    def volume(self) -> Optional[float]:
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
        return self.parameters.playback_volume

    @volume.setter
    def volume(self, value: Optional[float]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.Parameters,
                self._root.parameters,
                "playback_volume",
                value,
            )
            self._root.parameters.playback_volume = result
        else:
            self._root.parameters.playback_volume = value

    # =========================================================================

    @property
    def global_playback(self) -> Optional[bool]:
        """
        Whether or not to play this sound at a constant volume regardless of
        distance.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.parameters.playback_globally

    @global_playback.setter
    def global_playback(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.Parameters,
                self._root.parameters,
                "playback_globally",
                value,
            )
            self._root.parameters.playback_globally = result
        else:
            self._root.parameters.playback_globally = value

    # =========================================================================

    @property
    def show_alert(self) -> Optional[bool]:
        """
        Whether or not to show an alert to the player(s) if a sound is played.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.alert_parameters.show_alert

    @show_alert.setter
    def show_alert(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.AlertParameters,
                self._root.alert_parameters,
                "show_alert",
                value,
            )
            self._root.alert_parameters.show_alert = result
        else:
            self._root.alert_parameters.show_alert = value

    # =========================================================================

    @property
    def allow_polyphony(self) -> Optional[bool]:
        """
        Whether or not to allow the speaker to play multiple notes at once.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.parameters.allow_polyphony

    @allow_polyphony.setter
    def allow_polyphony(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.Parameters,
                self._root.parameters,
                "allow_polyphony",
                value,
            )
            self._root.parameters.allow_polyphony = result
        else:
            self._root.parameters.allow_polyphony = value

    # =========================================================================

    @property
    def show_alert_on_map(self) -> Optional[bool]:
        """
        Whether or not to show the alert on the map where the speaker lives.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """
        return self.alert_parameters.show_on_map

    @show_alert_on_map.setter
    def show_alert_on_map(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.AlertParameters,
                self._root.alert_parameters,
                "show_on_map",
                value,
            )
            self._root.alert_parameters.show_on_map = result
        else:
            self._root.alert_parameters.show_on_map = value

    # =========================================================================

    @property
    def alert_icon(self) -> Optional[SignalID]:
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
    def alert_icon(self, value: Union[str, SignalID, None]):  # TODO: SignalStr
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.AlertParameters,
                self._root.alert_parameters,
                "icon_signal_id",
                value,
            )
            self.alert_parameters["icon_signal_id"] = result
        else:
            self.alert_parameters["icon_signal_id"] = value

    # =========================================================================

    @property
    def alert_message(self) -> Optional[str]:
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
    def alert_message(self, value: Optional[str]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.AlertParameters,
                self.alert_parameters,
                "alert_message",
                value,
            )
            self._root.alert_parameters.alert_message = result
        else:
            self._root.alert_parameters.alert_message = value

    # =========================================================================

    @property
    def signal_value_is_pitch(self) -> Optional[bool]:
        """
        Whether or not the value of a signal determines the pitch of the note to
        play.

        :type: ``bool``

        :exception TypeError: If set to anything other than a ``bool`` or ``None``.
        """

        return self.control_behavior.circuit_parameters.signal_value_is_pitch

    @signal_value_is_pitch.setter
    def signal_value_is_pitch(self, value: Optional[bool]):
        if self.validate_assignment:
            result = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior.CircuitParameters,
                self.control_behavior.circuit_parameters,
                "signal_value_is_pitch",
                value,
            )
            self.control_behavior.circuit_parameters.signal_value_is_pitch = result
        else:
            self.control_behavior.circuit_parameters.signal_value_is_pitch = value

    # =========================================================================

    @property
    def instrument_id(self) -> Optional[int]:
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
        return self.control_behavior["circuit_parameters"]["instrument_id"]

    @instrument_id.setter
    def instrument_id(self, value: Optional[int]):
        if self.validate_assignment:
            value = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior.CircuitParameters,
                self.control_behavior.circuit_parameters,
                "instrument_id",
                value,
            )
            self.control_behavior.circuit_parameters.instrument_id = value
        else:
            self.control_behavior.circuit_parameters.instrument_id = value

        # new_name = self._instrument_names.get(value, {"self": None})["self"]
        # self.control_behavior.circuit_parameters.instrument_name = new_name

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
        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        """
        return (
            instruments_data.name_of.get(self.name, {})
            .get(self.instrument_id, {})
            .get("self", None)
        )

    @instrument_name.setter
    def instrument_name(self, value: Optional[str]):
        if self.validate_assignment:
            value = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior.CircuitParameters,
                self.control_behavior.circuit_parameters,
                "instrument_name",
                value,
            )

        if value is None:
            self.control_behavior.circuit_parameters.instrument_id = None
        else:
            new_id = (
                instruments_data.index_of.get(self.name, {})
                .get(value, {})
                .get("self", None)
            )
            self.control_behavior.circuit_parameters.instrument_id = new_id

    # =========================================================================

    @property
    def note_id(self) -> Optional[int]:
        """
        Numeric index of the note. Updated in tandem with ``note_name``.

        :getter: Gets the number of the current note, or ``None`` if not set.
        :setter: Sets the number of the current note. Removes the key if set to
            ``None``.

        :exception InvalidInstrumentID: If set to a number that is not
            recognized as a valid note index for this speaker.
        :exception TypeError: If set to anything other than an ``int`` or ``None``.
        """
        return self.control_behavior.circuit_parameters.note_id

    @note_id.setter
    def note_id(self, value: Optional[int]):
        if self.validate_assignment:
            value = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior.CircuitParameters,
                self.control_behavior.circuit_parameters,
                "note_id",
                value,
            )
            self.control_behavior.circuit_parameters.note_id = value
        else:
            self.control_behavior.circuit_parameters.note_id = value

    # =========================================================================

    @property
    def note_name(self) -> str:
        """
        Name of the note. Updated in tandem with ``note_id``. Not exported.

        :getter: Gets the name of the current instrument, or ``None`` if not set.
        :setter: Sets the name of the current instrument. Removes the key if set
            to ``None``.

        :exception InvalidInstrumentID: If set to a name that is not recognized
            as a valid instrument name for this speaker.
        :exception TypeError: If set to anything other than a ``str`` or ``None``.
        """
        return (
            instruments_data.name_of.get(self.name, {})
            .get(self.instrument_id, {})
            .get(self.note_id, None)
        )

    @note_name.setter
    def note_name(self, value: Optional[str]):
        if self.validate_assignment:
            value = attempt_and_reissue(
                self,
                type(self).Format.ControlBehavior.CircuitParameters,
                self.control_behavior.circuit_parameters,
                "note_name",
                value,
            )

        # We could do:
        # self.control_behavior.circuit_parameters.note_name = value
        # And then just return that in the getter...

        if value is None:
            self.control_behavior.circuit_parameters.note_id = None
        else:
            new_id = (
                instruments_data.index_of.get(self.name, {})
                .get(self.instrument_name, {})
                .get(value, None)
            )
            self.control_behavior.circuit_parameters.note_id = new_id

    # =========================================================================

    def merge(self, other: "ProgrammableSpeaker"):
        super().merge(other)

        self.parameters = other.parameters
        self.alert_parameters = other.alert_parameters

    # =========================================================================

    __hash__ = Entity.__hash__

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.parameters == other.parameters
            and self.alert_parameters == other.alert_parameters
        )
