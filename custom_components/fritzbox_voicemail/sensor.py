"""Sensor platform for Fritzbox Voicemail."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)

from .entity import IntegrationBlueprintEntity

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
    hass: HomeAssistant,
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


class FritzboxVoicemailSensor(IntegrationBlueprintEntity, SensorEntity):
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
    def native_value(self) -> int:
        """Return number of voicemail messages."""

        return len(self.coordinator.data["messages"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return voicemail messages as attributes."""

        return {
            "messages": self.coordinator.data["messages"],
        }