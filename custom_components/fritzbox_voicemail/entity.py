"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import FritzboxVoicemailDataUpdateCoordinator


class IntegrationBlueprintEntity(CoordinatorEntity[FritzboxVoicemailDataUpdateCoordinator]):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: FritzboxVoicemailDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._tam_name = f"Fritzbox Voicemail"
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name=self._tam_name
        )
