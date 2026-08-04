"""Sensor platform for Fritzbox Voicemail."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)

from .entity import FritzboxVoicemailEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FritzboxVoicemailDataUpdateCoordinator
    from .data import FritzboxVoicemailConfigEntry


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="voicemail_messages",
        name="Voicemail Messages",
        icon="mdi:forum",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: FritzboxVoicemailConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        FritzboxVoicemailSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class FritzboxVoicemailSensor(FritzboxVoicemailEntity, SensorEntity):
    """Fritzbox Voicemail sensor."""

    def __init__(
        self,
        coordinator: FritzboxVoicemailDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def _messages(self) -> list[dict[str, Any]]:
        """Return messages for this TAM."""
        all_messages = (self.coordinator.data or {}).get("messages", [])
        return [
            msg for msg in all_messages
            if str(msg.get("Tam", self.tam_index)) == str(self.tam_index)
        ]

    @property
    def native_value(self) -> int:
        """Return number of voicemail messages."""
        return len(self._messages)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return voicemail messages as attributes."""
        return {
            "messages": self._messages,
        }